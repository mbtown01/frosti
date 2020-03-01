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
    SensorDataChangedEvent, UserThermostatInteractionEvent


app = Flask(__name__, static_url_path='')


class ApiDataBroker(EventBusMember):
    """ Dedicated to responding to the REST API for the thermostat and
    brokering any necessary data/events """

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

        app.add_url_rule('/', 'serve_root', self.serve_root)
        app.add_url_rule('/main.css', 'serve_css', self.serve_css)
        app.add_url_rule(
            '/include/<path:path>', 'serve_static', self.serve_static)

        app.add_url_rule('/api/version', 'api_version', self.api_version)
        app.add_url_rule('/api/status', 'api_status', self.api_status)
        app.add_url_rule('/api/settings', 'api_settings', self.api_settings)

        app.add_url_rule(
            '/api/action/nextMode', 'api_action_next_mode',
            self.api_action_next_mode)
        app.add_url_rule(
            '/api/action/raiseComfort', 'api_action_raise_comfort',
            self.api_action_raise_comfort)
        app.add_url_rule(
            '/api/action/lowerComfort', 'api_next_lower_comfort',
            self.api_action_lower_comfort)

    def serve_root(self):
        return render_template(
            'index.html',
            temperature=f'{self.__lastTemperature}',
            pressure=f'{self.__lastPressure}',
            humidity=f'{self.__lastHumidity}',
        )

    def serve_css(self):
        return render_template('main.css')

    def serve_static(self, path: str):
        return send_from_directory('include', path)

    def api_version(self):
        return 'rpt-0.1'

    def api_status(self):
        response = {
            'version': self.api_version(),
            'sensors': {
                'temperature': self.__lastTemperature,
                'pressure': self.__lastPressure,
                'humidity': self.__lastHumidity,
            },
            'state': str(self.__lastState).replace('ThermostatState.', ''),
        }
        return json.dumps(response, indent=4)

    def api_settings(self):
        settings = self._getService(Settings)

        response = {
            'version': self.api_version(),
            'comfortMin': settings.comfortMin,
            'comfortMax': settings.comfortMax,
            'mode': str(settings.mode).replace('Mode.', ''),
        }
        return json.dumps(response, indent=4)

    def api_action_next_mode(self):
        self._fireEvent(UserThermostatInteractionEvent(
            UserThermostatInteractionEvent.MODE_NEXT))

    def api_action_raise_comfort(self):
        self._fireEvent(UserThermostatInteractionEvent(
            UserThermostatInteractionEvent.COMFORT_RAISE))

    def api_action_lower_comfort(self):
        self._fireEvent(UserThermostatInteractionEvent(
            UserThermostatInteractionEvent.COMFORT_LOWER))

    def __processThermostatStateChanged(
            self, event: ThermostatStateChangedEvent):
        self.__lastState = event.state

    def __processSensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.__lastPressure = event.pressure
        self.__lastHumidity = event.humidity


# class ApiMessageHandler:
#     apiDataBroker = None

#     @staticmethod
#     def setup(eventHandler: ApiDataBroker):
#         __class__.apiDataBroker = eventHandler

#     # region Static webserice handlers
#     @staticmethod
#     @app.route("/")
#     def serve_root():
#         return render_template(
#             'index.html',
#             temperature=f'{__class__.apiDataBroker.temperature}',
#             pressure=f'{__class__.apiDataBroker.pressure}',
#             humidity=f'{__class__.apiDataBroker.humidity}',
#         )

#     @staticmethod
#     @app.route("/main.css")
#     def serve_css():
#         return render_template('main.css')

#     @staticmethod
#     @app.route('/include/<path:path>')
#     def serve_static(path):
#         return send_from_directory('include', path)

#     @staticmethod
#     @app.route('/api/version')
#     def api_version():
#         return __class__.apiDataBroker.version

#     @staticmethod
#     @app.route('/api/status')
#     def api_status():
#         return __class__.apiDataBroker.getStatusJson()

#     @staticmethod
#     @app.route('/api/settings')
#     def api_settings():
#         return __class__.apiDataBroker.getSettingsJson()

#     @staticmethod
#     @app.route('/api/action/nextMode', methods=['POST'])
#     def api_action_next_mode():
#         return __class__.apiDataBroker.nextMode()

#     @staticmethod
#     @app.route('/api/action/raiseComfort', methods=['POST'])
#     def api_action_raise_comfort():
#         return __class__.apiDataBroker.raiseComfort()

#     @staticmethod
#     @app.route('/api/action/lowerComfort', methods=['POST'])
#     def api_action_lower_comfort():
#         return __class__.apiDataBroker.lowerComfort()

#     # endregion
