from flask import Flask, request
from flask_cors import CORS
from threading import Thread
import json

from .ThermostatService import ThermostatService
from src.logging import log, handleException
from src.core import ServiceProvider, ServiceConsumer, EventBus, \
    ThermostatState
from src.core.events import \
    ThermostatStateChangedEvent, \
    SensorDataChangedEvent, UserThermostatInteractionEvent


class ApiDataBrokerService(ServiceConsumer):
    """ Dedicated to responding to the REST API for the thermostat and
    brokering any necessary data/events """

    def __init__(self,):
        self.__app = Flask(__name__, static_url_path='')

        self.__app.add_url_rule(
            '/api/version', 'api_version', self.api_version)
        self.__app.add_url_rule(
            '/api/status', 'api_status', self.api_status)

        self.__app.add_url_rule(
            '/api/action/nextMode', 'api_action_next_mode',
            self.api_action_next_mode, methods=['POST'])
        self.__app.add_url_rule(
            '/api/action/raiseComfort', 'api_action_raise_comfort',
            self.api_action_raise_comfort, methods=['POST'])
        self.__app.add_url_rule(
            '/api/action/lowerComfort', 'api_next_lower_comfort',
            self.api_action_lower_comfort, methods=['POST'])

        self.__cors = CORS(self.__app)

        self.__flaskThread = Thread(
            target=self.__flaskEntryPoint,
            name='Flask Driver')
        self.__flaskThread.daemon = True
        self.__flaskThread.start()

        self.__lastState = ThermostatState.OFF
        self.__lastTemperature = 0
        self.__lastPressure = 0
        self.__lastHumidity = 0

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        eventBus = self._getService(EventBus)
        eventBus.installEventHandler(
            SensorDataChangedEvent, self.__processSensorDataChanged)
        eventBus.installEventHandler(
            ThermostatStateChangedEvent, self.__processThermostatStateChanged)

    def __processThermostatStateChanged(
            self, event: ThermostatStateChangedEvent):
        self.__lastState = event.state

    def __processSensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.__lastPressure = event.pressure
        self.__lastHumidity = event.humidity

    def __flaskEntryPoint(self):
        try:
            self.__app.run("0.0.0.0", 5000)
            log.error("Somehow we exited the Flask thread")
        except:
            handleException("starting flask")

    def __getStatus(self):
        thermostatService = self._getService(ThermostatService)

        response = {
            'version': self.api_version(),
            'sensors': {
                'temperature': f"{self.__lastTemperature}",
                'pressure': f"{self.__lastPressure}",
                'humidity': f"{self.__lastHumidity}",
            },
            'comfortMin': thermostatService.comfortMin,
            'comfortMax': thermostatService.comfortMax,
            'state': str(thermostatService.state),
            'mode': str(thermostatService.mode)
        }
        return json.dumps(response, indent=4)

    def __changeComfortMax(self, offset: int = 1.0):
        thermostatService = self._getService(ThermostatService)
        thermostatService.comfortMax += offset
        return self.__getStatus()

    def api_version(self):
        return 'rpt-0.1'

    def api_status(self):
        eventBus = self._getService(EventBus)
        return eventBus.safeInvoke(self.__getStatus)

    def api_action_next_mode(self):
        eventBus = self._getService(EventBus)
        eventBus.fireEvent(UserThermostatInteractionEvent(
            UserThermostatInteractionEvent.MODE_NEXT))
        return eventBus.safeInvoke(self.__getStatus)

    def api_action_raise_comfort(self):
        eventBus = self._getService(EventBus)
        offset = float(request.args.get('offset', 1.0))
        return eventBus.safeInvoke(self.__changeComfortMax, offset=offset)

    def api_action_lower_comfort(self):
        eventBus = self._getService(EventBus)
        eventBus.fireEvent(UserThermostatInteractionEvent(
            UserThermostatInteractionEvent.COMFORT_LOWER))
        return eventBus.safeInvoke(self.__getStatus)
