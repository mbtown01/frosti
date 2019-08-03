from flask import Flask, render_template, request, send_from_directory
from flask.logging import default_handler
from threading import Thread
import logging
import json

from src.logging import log
from src.settings import Settings
from src.events import Event, EventBus, EventHandler
from src.thermostat import PropertyChangedEvent, \
    ThermostatStateChangedEvent, ThermostatState, \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


app = Flask(__name__, static_url_path='')


class ApiEventHandler(EventHandler):
    """ Event handler thread dedicated to responding to the REST API for
    the thermostat.
    """
    __instance = None

    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus)

        self.__flaskThread = Thread(
            target=app.run,
            name='Flask Driver',
            args=("0.0.0.0", 5000))
        self.__flaskThread.daemon = True
        self.__flaskThread.start()

        self.__lastState = ThermostatState.OFF
        self.__lastTemperature = 0
        self.__lastPressure = 0
        self.__lastHumidity = 0

        super()._subscribe(
            TemperatureChangedEvent, self.__processTemperatureChanged)
        super()._subscribe(
            PressureChangedEvent, self.__processPressureChanged)
        super()._subscribe(
            HumidityChangedEvent, self.__processHumidityChanged)
        super()._subscribe(
            ThermostatStateChangedEvent, self.__processThermostatStateChanged)

    def __processThermostatStateChanged(
            self, event: ThermostatStateChangedEvent):
        self.__lastState = event.state

    def __processTemperatureChanged(self, event: TemperatureChangedEvent):
        self.__lastTemperature = event.value

    def __processPressureChanged(self, event: PressureChangedEvent):
        self.__lastPressure = event.value

    def __processHumidityChanged(self, event: HumidityChangedEvent):
        self.__lastHumidity = event.value

    @property
    def version(self):
        return 'rpt-0.1'

    @property
    def temperature(self):
        return self.__lastTemperature

    @property
    def pressure(self):
        return self.__lastPressure

    @property
    def humidity(self):
        return self.__lastHumidity

    def toggleMode(self):
        Settings.instance().mode = Settings.Mode(
            (int(Settings.instance().mode.value)+1) % len(Settings.Mode))

    def getStatusJson(self):
        response = {
            'version': self.version,
            'sensors': {
                'temperature': self.temperature,
                'pressure': self.pressure,
                'humidity': self.humidity,
            },
            'state': str(self.__lastState),
        }
        return json.dumps(response, indent=4)

    def getSettingsJson(self):
        response = {
            'version': self.version,
            'comfortMin': Settings.instance().comfortMin,
            'comfortMax': Settings.instance().comfortMax,
            'mode': str(Settings.instance().mode),
            'delta': Settings.instance().delta,
        }
        return json.dumps(response, indent=4)

    @staticmethod
    def createInstance(eventBus: EventBus):
        """ Send SettingsChangedEvent notifications to the provided event bus,
        or nowhere if eventBus is None
        """
        __class__.__instance = ApiEventHandler(eventBus)

    @staticmethod
    def instance():
        """ Returns the global instance
        """
        if __class__.__instance is None:
            raise RuntimeError("Instance of ApiEventHandler not instantiated")
        return __class__.__instance

    # region Static webserice handlers

    @staticmethod
    @app.route("/")
    def serve_root():
        return render_template(
            'index.html',
            temperature=f'{ApiEventHandler.instance().temperature}',
            pressure=f'{ApiEventHandler.instance().pressure}',
            humidity=f'{ApiEventHandler.instance().humidity}',
        )

    @staticmethod
    @app.route('/js/<path:path>')
    def serve_static(path):
        return send_from_directory('js', path)

    @staticmethod
    @app.route('/api/version')
    def api_version():
        return ApiEventHandler.instance().version

    @staticmethod
    @app.route('/api/status')
    def api_status():
        return ApiEventHandler.instance().getStatusJson()

    @staticmethod
    @app.route('/api/settings')
    def api_settings():
        return ApiEventHandler.instance().getSettingsJson()

    @staticmethod
    @app.route('/api/action/mode_toggle', methods=['POST'])
    def api_action_mode_toggle():
        ApiEventHandler.instance().toggleMode()
        return None

    @staticmethod
    @app.route('/api/sensors/temperature')
    def api_sensor_temperature():
        return f"{ApiEventHandler.instance().temperature}"

    @staticmethod
    @app.route('/api/sensors/pressure')
    def api_sensor_pressure():
        return f"{ApiEventHandler.instance().pressure}"

    @staticmethod
    @app.route('/api/sensors/humidity')
    def api_sensor_humidity():
        return f"{ApiEventHandler.instance().humidity}"

    # endregion
