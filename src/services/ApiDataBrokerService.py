from flask import Flask, request, abort
from flask_cors import CORS
from functools import wraps
from threading import Thread
from random import getrandbits
import json

from .ThermostatService import ThermostatService
from src.logging import log, handleException
from src.core import ServiceProvider, ServiceConsumer, EventBus, \
    ThermostatState
from src.core.events import \
    ThermostatStateChangedEvent, \
    SensorDataChangedEvent

VALID_API_KEYS = list()


def require_appkey(method):
    """ Decorator for identifying an API method that requets a key """
    @wraps(method)
    def decoratedMethod(*args, **kwargs):
        if request.args.get('key', 'none') in VALID_API_KEYS:
            return method(*args, **kwargs)
        abort(401)

    return decoratedMethod


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
            '/api/action/stop', 'api_action_stop',
            self.api_action_stop, methods=['POST'])

        self.__app.add_url_rule(
            '/api/action/nextMode', 'api_action_next_mode',
            self.api_action_next_mode, methods=['POST'])
        self.__app.add_url_rule(
            '/api/action/raiseComfort', 'api_action_raise_comfort',
            self.api_action_raise_comfort, methods=['POST'])
        self.__app.add_url_rule(
            '/api/action/lowerComfort', 'api_next_lower_comfort',
            self.api_action_lower_comfort, methods=['POST'])
        self.__app.add_url_rule(
            '/api/action/changeComfort', 'api_next_change_comfort',
            self.api_action_change_comfort, methods=['POST'])

        self.__cors = CORS(self.__app)

        self.__flaskThread = Thread(
            target=self.__flaskEntryPoint,
            name='Flask Driver')
        self.__flaskThread.daemon = True
        self.__flaskThread.start()

        self.__lastState = ThermostatState.OFF
        self.__lastSensorData = None
        self.__sessionApiKey = f"{getrandbits(256):x}"
        VALID_API_KEYS.append(self.__sessionApiKey)

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        self.__eventBus = self._getService(EventBus)
        self.__eventBus.installEventHandler(
            SensorDataChangedEvent, self.__processSensorDataChanged)
        self.__eventBus.installEventHandler(
            ThermostatStateChangedEvent, self.__processThermostatStateChanged)

    @property
    def sessionApiKey(self):
        return self.__sessionApiKey

    def __processThermostatStateChanged(
            self, event: ThermostatStateChangedEvent):
        self.__lastState = event.state

    def __processSensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastSensorData = event

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
            'comfortMin': thermostatService.comfortMin,
            'comfortMax': thermostatService.comfortMax,
            'currentProgram': thermostatService.currentProgramName,
            'isInPriceOverride': thermostatService.isInPriceOverride,
            'state': str(thermostatService.state),
            'mode': str(thermostatService.mode)
        }

        if self.__lastSensorData is not None:
            response['sensors'] = {
                'temperature': f"{self.__lastSensorData.temperature}",
                'pressure': f"{self.__lastSensorData.pressure}",
                'humidity': f"{self.__lastSensorData.humidity}",
            }

        return json.dumps(response, indent=4)

    def __modifyComfortSettings(self, offset: int = 0, value: int = -1):
        thermostatService = self._getService(ThermostatService)
        thermostatService.modifyComfortSettings(offset=offset, value=value)
        return self.__getStatus()

    def __nextMode(self):
        thermostatService = self._getService(ThermostatService)
        thermostatService.nextMode()
        return self.__getStatus()

    def api_version(self):
        return 'rpt-0.1'

    def api_status(self):
        return self.__eventBus.safeInvoke(self.__getStatus)

    def api_action_next_mode(self):
        return self.__eventBus.safeInvoke(self.__nextMode)

    def api_action_raise_comfort(self):
        offset = float(request.args.get('offset', 1.0))
        return self.__eventBus.safeInvoke(
            self.__modifyComfortSettings, offset=offset)

    def api_action_lower_comfort(self):
        offset = float(request.args.get('offset', 1.0))
        return self.__eventBus.safeInvoke(
            self.__modifyComfortSettings, offset=-offset)

    def api_action_change_comfort(self):
        offset = float(request.args.get('offset', 0.0))
        value = float(request.args.get('value', -1.0))
        return self.__eventBus.safeInvoke(
            self.__modifyComfortSettings, offset=offset, value=value)

    @require_appkey
    def api_action_stop(self):
        VALID_API_KEYS.remove(self.__sessionApiKey)
        status = self.__eventBus.safeInvoke(self.__getStatus)
        self.__eventBus.stop()
        shutdownMethod = request.environ.get('werkzeug.server.shutdown')
        return status
