from flask import Flask, render_template, request, send_from_directory
from flask.logging import default_handler
from threading import Thread
import logging
import json

from src.logging import log
from src.settings import Settings
from src.services import ServiceProvider
from src.events import Event, EventBus, EventBusMember
from src.generics import PropertyChangedEvent, \
    ThermostatStateChangedEvent, ThermostatState, \
    SensorDataChangedEvent


app = Flask(__name__, static_url_path='')


class ApiDataBroker(EventBusMember):
    """ Thread dedicated to responding to the REST API for the thermostat and
    brokering any necessary data/events """
    __instance = None

    def __init__(self,):
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

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)
        super()._installEventHandler(
            SensorDataChangedEvent, self.__processSensorDataChanged)
        super()._installEventHandler(
            ThermostatStateChangedEvent, self.__processThermostatStateChanged)

    def __processThermostatStateChanged(
            self, event: ThermostatStateChangedEvent):
        self.__lastState = event.state

    def __processSensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.__lastPressure = event.pressure
        self.__lastHumidity = event.humidity

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
        settings = self._getService(Settings)

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
        settings = self._getService(Settings)

        response = {
            'version': self.version,
            'comfortMin': settings.comfortMin,
            'comfortMax': settings.comfortMax,
            'mode': str(settings.mode).replace('Mode.', ''),
        }
        return json.dumps(response, indent=4)


class ApiMessageHandler:
    apiDataBroker = None

    @staticmethod
    def setup(eventHandler: ApiDataBroker):
        __class__.apiDataBroker = eventHandler

    # region Static webserice handlers
    @staticmethod
    @app.route("/")
    def serve_root():
        return render_template(
            'index.html',
            temperature=f'{__class__.apiDataBroker.temperature}',
            pressure=f'{__class__.apiDataBroker.pressure}',
            humidity=f'{__class__.apiDataBroker.humidity}',
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
        return __class__.apiDataBroker.version

    @staticmethod
    @app.route('/api/status')
    def api_status():
        return __class__.apiDataBroker.getStatusJson()

    @staticmethod
    @app.route('/api/settings')
    def api_settings():
        return __class__.apiDataBroker.getSettingsJson()

    @staticmethod
    @app.route('/api/action/mode_toggle', methods=['POST'])
    def api_action_mode_toggle():
        return __class__.apiDataBroker.toggleMode()

    # endregion
