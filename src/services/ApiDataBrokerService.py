from flask import Flask, Response, request, abort
from flask_cors import CORS
from functools import wraps
from threading import Thread
from random import getrandbits
import json

from .ThermostatService import ThermostatService
from .OrmManagementService import OrmManagementService
from src.logging import log, handleException
from src.core import ServiceProvider, ServiceConsumer, EventBus, \
    ThermostatState
from src.core.events import ThermostatStateChangedEvent, SensorDataChangedEvent
from src.core.orm import OrmConfig

VALID_API_KEYS = list()
API_VERSION = 'rpt-v0.2'


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
    brokering any necessary data/events

    https://docs.microsoft.com/en-us/azure/architecture/best-practices/api-design

    Some summaries of the above:
        * GET retrieves a representation of the resource at the specified URI.
          The body of the response message contains the details of the
          requested resource.
        * POST creates a new resource at the specified URI. The body of the
          request message provides the details of the new resource. Note that
          POST can also be used to trigger operations that don't actually
          create resources.
        * PUT either creates or replaces the resource at the specified URI.
          The body of the request message specifies the resource to be created
          or updated.
        * PATCH performs a partial update of a resource. The request body
          specifies the set of changes to apply to the resource
        * DELETE removes the resource at the specified URI.
    """

    def __init__(self,):
        self.__app = Flask(__name__, static_url_path='')

        self.__app.add_url_rule(
            '/api/status', view_func=self.__apiStatus)

        self.__app.add_url_rule(
            '/api/config', view_func=self.__apiConfig,
            methods=['GET', 'POST', 'PUT'])
        self.__app.add_url_rule(
            '/api/config/<name>', view_func=self.__apiConfig,
            methods=['GET', 'POST', 'PUT', 'DELETE'])

        self.__app.add_url_rule(
            '/api/action/stop',
            view_func=self.__apiActionStop, methods=['POST'])
        self.__app.add_url_rule(
            '/api/action/nextMode',
            view_func=self.__apiActionNextMode, methods=['POST'])
        self.__app.add_url_rule(
            '/api/action/changeComfort',
            view_func=self.__apiActionChangeComfort, methods=['POST'])

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

    def getStatus(self):
        thermostatService = self._getService(ThermostatService)

        response = {
            'version': API_VERSION,
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

        return response

    def getConfig(self):
        ormManagementService = self._getService(OrmManagementService)

        results = ormManagementService.session.query(OrmConfig)
        return {a.name: a.value for a in results}

    def setConfig(self, data: dict):
        ormManagementService = self._getService(OrmManagementService)

        results = ormManagementService.session.query(OrmConfig) \
            .filter(OrmConfig.name.in_(data.keys()))
        for ormConfigEntry in results:
            ormConfigEntry.value = data[ormConfigEntry.name]
            data.pop(ormConfigEntry.name)
        for name, value in data.items():
            configEntry = OrmConfig()
            configEntry.name = name
            configEntry.value = value
            ormManagementService.session.add(configEntry)

        ormManagementService.session.commit()

    def modifyComfortSettings(self, offset: int = 0, value: int = -1):
        thermostatService = self._getService(ThermostatService)
        thermostatService.modifyComfortSettings(offset=offset, value=value)

    def nextMode(self):
        thermostatService = self._getService(ThermostatService)
        thermostatService.nextMode()

    # region Flask API calls, all happening on a different thread

    def __apiResponse(self, data, status=200):
        mimeType = 'application/json'
        jsonText = json.dumps(data, indent=4)
        response = Response(jsonText, status=status, mimetype=mimeType)
        return response

    def __apiStatus(self):
        data = self.__eventBus.safeInvoke(self.getStatus)
        return self.__apiResponse(data)

    def __apiConfig(self, name: str = None):
        """ If name is not null, use it as the key for the config value,
        otherwise assume the request is the contents of the entire config """

        if 'GET' == request.method:
            # Gets the value of the named config item, or all items
            data = self.__eventBus.safeInvoke(self.getConfig)
            if name is not None:
                data = {name: data.get(name)}
            return self.__apiResponse(data)

        if request.method in ['PUT', 'POST']:
            # Sets the value of the named config item, or all items
            data = request.get_json()
            if name is not None:
                data = {name: data}
            self.__eventBus.safeInvoke(self.setConfig, data)
            return self.__apiResponse(data)

    def __apiActionNextMode(self):
        self.__eventBus.safeInvoke(self.nextMode)
        return self.__apiStatus()

    def __apiActionChangeComfort(self):
        offset = float(request.args.get('offset', 0.0))
        value = float(request.args.get('value', -1.0))
        self.__eventBus.safeInvoke(
            self.modifyComfortSettings, offset=offset, value=value)
        return self.__apiStatus()

    @require_appkey
    def __apiActionStop(self):
        VALID_API_KEYS.remove(self.__sessionApiKey)
        data = self.__eventBus.safeInvoke(self.getStatus)
        response = self.__apiResponse(data)
        self.__eventBus.stop()
        return response

    # endregion

    def __flaskEntryPoint(self):
        try:
            self.__app.run("0.0.0.0", 5000)
            log.error("Somehow we exited the Flask thread")
        except:
            handleException("starting flask")
