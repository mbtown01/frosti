from flask import Flask, render_template, send_from_directory
from threading import Thread
import json

from .SettingsService import SettingsService
from src.core import ServiceProvider, EventBusMember, \
    ThermostatState
from src.core.events import \
    ThermostatStateChangedEvent, \
    SensorDataChangedEvent, UserThermostatInteractionEvent


class ApiDataBrokerService(EventBusMember):
    """ Dedicated to responding to the REST API for the thermostat and
    brokering any necessary data/events """

    def __init__(self,):
        self.__app = Flask(
            __name__, static_url_path='', template_folder='../templates')
        self.__app.add_url_rule(
            '/', 'serve_root', self.serve_root)
        self.__app.add_url_rule(
            '/main.css', 'serve_css', self.serve_css)
        self.__app.add_url_rule(
            '/include/<path:path>', 'serve_static', self.serve_static)

        self.__app.add_url_rule(
            '/api/version', 'api_version', self.api_version)
        self.__app.add_url_rule(
            '/api/status', 'api_status', self.api_status)
        self.__app.add_url_rule(
            '/api/settings', 'api_settings', self.api_settings)

        self.__app.add_url_rule(
            '/api/action/nextMode', 'api_action_next_mode',
            self.api_action_next_mode, methods=['POST'])
        self.__app.add_url_rule(
            '/api/action/raiseComfort', 'api_action_raise_comfort',
            self.api_action_raise_comfort, methods=['POST'])
        self.__app.add_url_rule(
            '/api/action/lowerComfort', 'api_next_lower_comfort',
            self.api_action_lower_comfort, methods=['POST'])

        self.__flaskThread = Thread(
            target=self.__app.run,
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
        return send_from_directory('../include', path)

    def api_version(self):
        return 'rpt-0.1'

    def api_status(self):
        response = {
            'version': self.api_version(),
            'sensors': {
                'temperature': f"{self.__lastTemperature:.1f}",
                'pressure': f"{self.__lastPressure:.1f}",
                'humidity': f"{self.__lastHumidity:.1f}",
            },
            'state': str(self.__lastState).replace('ThermostatState.', ''),
        }
        return json.dumps(response, indent=4)

    def api_settings(self):
        settings = self._getService(SettingsService)

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
        return ""

    def api_action_raise_comfort(self):
        self._fireEvent(UserThermostatInteractionEvent(
            UserThermostatInteractionEvent.COMFORT_RAISE))
        return ""

    def api_action_lower_comfort(self):
        self._fireEvent(UserThermostatInteractionEvent(
            UserThermostatInteractionEvent.COMFORT_LOWER))
        return ""

    def __processThermostatStateChanged(
            self, event: ThermostatStateChangedEvent):
        self.__lastState = event.state

    def __processSensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.__lastPressure = event.pressure
        self.__lastHumidity = event.humidity
