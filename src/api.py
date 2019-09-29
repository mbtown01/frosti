from flask import Flask, render_template, request, send_from_directory
from flask.logging import default_handler
from threading import Thread
import logging
import json

from src.logging import log
from src.settings import settings, Settings
from src.events import Event, EventBus, EventHandler
from src.generics import PropertyChangedEvent, \
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
        settings.mode = Settings.Mode(
            (int(settings.mode.value)+1) % len(Settings.Mode))
        return f"Mode now {settings.mode}"

    def getStatusJson(self):
        response = {
            'version': self.version,
            'sensors': {
                'temperature': self.temperature,
                'pressure': self.pressure,
                'humidity': self.humidity,
            },
            'state': str(self.__lastState).replace('ThermostatState.', ''),
        }
        return json.dumps(response, indent=4)

    def getSettingsJson(self):
        response = {
            'version': self.version,
            'comfortMin': settings.comfortMin,
            'comfortMax': settings.comfortMax,
            'mode': str(settings.mode).replace('Mode.', ''),
        }
        return json.dumps(response, indent=4)


class ApiMessageHandler:
    apiEventHandler = None

    @staticmethod
    def setup(eventHandler: ApiEventHandler):
        __class__.apiEventHandler = eventHandler

    # region Static webserice handlers
    @staticmethod
    @app.route("/")
    def serve_root():
        return render_template(
            'index.html',
            temperature=f'{__class__.apiEventHandler.temperature}',
            pressure=f'{__class__.apiEventHandler.pressure}',
            humidity=f'{__class__.apiEventHandler.humidity}',
        )

    @staticmethod
    @app.route("/main.css")
    def serve_css():
        return render_template('main.css')

    @staticmethod
    @app.route('/include/<path:path>')
    def serve_static(path):
        return send_from_directory('include', path)

    @staticmethod
    @app.route('/api/version')
    def api_version():
        return __class__.apiEventHandler.version

    @staticmethod
    @app.route('/api/status')
    def api_status():
        return __class__.apiEventHandler.getStatusJson()

    @staticmethod
    @app.route('/api/settings')
    def api_settings():
        return __class__.apiEventHandler.getSettingsJson()

    @staticmethod
    @app.route('/api/action/mode_toggle', methods=['POST'])
    def api_action_mode_toggle():
        return __class__.apiEventHandler.toggleMode()

    @staticmethod
    @app.route('/api/sensors/temperature')
    def api_sensor_temperature():
        return f"{__class__.apiEventHandler.temperature}"

    @staticmethod
    @app.route('/api/sensors/pressure')
    def api_sensor_pressure():
        return f"{__class__.apiEventHandler.pressure}"

    @staticmethod
    @app.route('/api/sensors/humidity')
    def api_sensor_humidity():
        return f"{__class__.apiEventHandler.humidity}"

    # endregion
