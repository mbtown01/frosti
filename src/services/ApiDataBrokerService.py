from flask import Flask, Response, request, abort
from flask_cors import CORS
from functools import wraps
from threading import Thread
from random import getrandbits
import uuid
import json

from .ThermostatService import ThermostatService
from .OrmManagementService import OrmManagementService
from src.logging import log, handleException
from src.core import ServiceProvider, ServiceConsumer, EventBus, \
    ThermostatState
from src.core.events import ThermostatStateChangedEvent, SensorDataChangedEvent
from src.core.orm import OrmConfig, OrmProgram, OrmSchedule, \
    OrmPriceOverride, OrmScheduleDay, OrmScheduleTime

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
    brokering any necessary data/events.

    This service owns the Flask thread that is monitoring incoming requests.
    All web API requests are given to the main event thread for processing.
    """

    def __init__(self):
        self.__app = Flask(__name__, static_url_path='')

        self.__app.add_url_rule(
            '/api/v1/status', view_func=self.__apiStatus, methods=['GET'])

        self.__app.add_url_rule(
            '/api/v1/config', view_func=self.__apiConfig,
            methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
        self.__app.add_url_rule(
            '/api/v1/config/<name>', view_func=self.__apiConfig,
            methods=['GET', 'PUT', 'PATCH', 'DELETE'])
        self.__app.add_url_rule(
            '/api/v1/programs', view_func=self.__apiPrograms,
            methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
        self.__app.add_url_rule(
            '/api/v1/programs/<name>', view_func=self.__apiPrograms,
            methods=['GET', 'PUT', 'PATCH', 'DELETE'])
        self.__app.add_url_rule(
            '/api/v1/schedules', view_func=self.__apiSchedules,
            methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
        self.__app.add_url_rule(
            '/api/v1/schedules/<name>', view_func=self.__apiSchedules,
            methods=['GET', 'PUT', 'PATCH', 'DELETE'])
        self.__app.add_url_rule(
            '/api/v1/actions', view_func=self.__apiActions,
            methods=['GET'])
        self.__app.add_url_rule(
            '/api/v1/actions/<name>', view_func=self.__apiActions,
            methods=['POST'])

        self.__app.add_url_rule(
            '/api/v1/action/stop',
            view_func=self.__apiActionStop, methods=['POST'])
        self.__app.add_url_rule(
            '/api/v1/action/nextMode',
            view_func=self.__apiActionNextMode, methods=['POST'])
        self.__app.add_url_rule(
            '/api/v1/action/changeComfort',
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

    def __upsertEntities(
            self, entityClass, updateMethod, data: dict, patch: bool):
        ormManagementService = self._getService(OrmManagementService)

        if not patch:
            ormManagementService.session.query(entityClass).delete()
        results = ormManagementService.session.query(entityClass) \
            .filter(entityClass.name.in_(data.keys()))
        for entity in results:
            updateMethod(entity, entity.name, data[entity.name])
            data.pop(entity.name)
        for name, value in data.items():
            entity = entityClass()
            updateMethod(entity, name, value)
            ormManagementService.session.add(entity)

        ormManagementService.session.commit()

    def setConfig(self, data: dict, patch: bool = False):
        def updateOrmConfig(ormConfig: OrmConfig, name: str, update: dict):
            ormConfig.name = name
            ormConfig.value = data[name]

        self.__upsertEntities(OrmConfig, updateOrmConfig, data, patch)

    def getPrograms(self):
        ormManagementService = self._getService(OrmManagementService)

        results = ormManagementService.session.query(OrmProgram)
        return {program.name: {
            'guid': str(program.guid),
            'comfortMin': program.comfort_min,
            'comfortMax': program.comfort_max,
            'priceOverrides': list({
                'price': override.price,
                'comfortMin': override.comfort_min,
                'comfortMax': override.comfort_max,
            } for override in program.overrides)
        } for program in results}

    def setPrograms(self, data: dict, patch: bool = False):
        ormManagementService = self._getService(OrmManagementService)

        def updateOrmProgram(ormProgram: OrmProgram, name: str, update: dict):
            ormProgram.name = name
            ormProgram.guid = uuid.uuid4()
            ormProgram.comfort_min = update.get('comfortMin')
            ormProgram.comfort_max = update.get('comfortMax')
            for child in ormProgram.overrides:
                ormManagementService.session.delete(child)
            for override in update.get('priceOverrides', list()):
                ormPriceOverride = OrmPriceOverride()
                ormPriceOverride.program_guid = ormProgram.guid
                ormPriceOverride.price = override['price']
                ormPriceOverride.comfort_min = override.get('comfortMin')
                ormPriceOverride.comfort_max = override.get('comfortMax')
                ormManagementService.session.add(ormPriceOverride)

        self.__upsertEntities(OrmProgram, updateOrmProgram, data, patch)

    def getSchedules(self):
        ormManagementService = self._getService(OrmManagementService)

        results = ormManagementService.session.query(OrmSchedule)
        return {schedule.name: {
            'guid': str(schedule.guid),
            'days': list(day.day for day in schedule.days),
            'times': list({
                'hour': time.hour,
                'minute': time.minute,
                'program': time.program.name,
            } for time in schedule.times)
        } for schedule in results}

    def setSchedules(self, data: dict, patch: bool = False):
        ormManagementService = self._getService(OrmManagementService)

        def updateOrmSchedule(
                ormSchedule: OrmSchedule, name: str, update: dict):
            programNameMap = {
                a.name: a.guid for a in
                ormManagementService.session.query(OrmProgram)}

            ormSchedule.name = name
            ormSchedule.guid = uuid.uuid4()
            for child in ormSchedule.days:
                ormManagementService.session.delete(child)
            for child in ormSchedule.times:
                ormManagementService.session.delete(child)
            for day in update.get('days', list()):
                ormScheduleDay = OrmScheduleDay()
                ormScheduleDay.schedule_guid = ormSchedule.guid
                ormScheduleDay.day = day
                ormManagementService.session.add(ormScheduleDay)
            for time in update.get('times', list()):
                ormScheduleTime = OrmScheduleTime()
                ormScheduleTime.schedule_guid = ormSchedule.guid
                ormScheduleTime.program_guid = \
                    programNameMap[time['program']]
                ormScheduleTime.hour = time['hour']
                ormScheduleTime.minute = time['minute']
                ormManagementService.session.add(ormScheduleTime)

        self.__upsertEntities(OrmSchedule, updateOrmSchedule, data, patch)

    def modifyComfortSettings(self, offset: int = 0, value: int = -1):
        thermostatService = self._getService(ThermostatService)
        thermostatService.modifyComfortSettings(offset=offset, value=value)

    def nextMode(self):
        thermostatService = self._getService(ThermostatService)
        thermostatService.nextMode()

    def __apiResponse(self, data, status=200):
        mimeType = 'application/json'
        jsonText = json.dumps(data, indent=4)
        response = Response(jsonText, status=status, mimetype=mimeType)
        return response

    def __apiStatus(self):
        data = self.__eventBus.safeInvoke(self.getStatus)
        return self.__apiResponse(data)

    def __apiServiceNamedDictionaryRequest(self, name, getMethod, setMethod):
        """ If name is not null, use it as the dictionary key value,
        otherwise assume the request is the contents of the entire config
        """
        if 'GET' == request.method:
            data = self.__eventBus.safeInvoke(getMethod)
            if name is None:
                return self.__apiResponse(data)
            if name not in data:
                return self.__apiResponse(dict(), 404)
            return self.__apiResponse(data[name])

        # Request a new entity be created with name provided in the entity
        # data, but only at the root end point and never at a named end point
        if 'POST' == request.method:
            data = request.get_json()
            if name is not None:
                response = {'ErrorText': 'POST not supported for named entity'}
                return self.__apiResponse(response, 400)
            dataMap = {data['name']: data}
            self.__eventBus.safeInvoke(setMethod, dataMap, patch=True)
            return self.__apiResponse(data)

        if 'PUT' == request.method:
            data = request.get_json()
            if name is not None:
                data = {name: data}
            self.__eventBus.safeInvoke(setMethod, data)
            return self.__apiResponse(data)

        if 'PATCH' == request.method:
            data = request.get_json()
            if name is not None:
                data = {name: data}
            self.__eventBus.safeInvoke(setMethod, data, patch=True)
            return self.__apiResponse(data)

        if 'DELETE' == request.method:
            data = request.get_json()
            if name is None:
                response = {'ErrorText': 'A name must be provided'}
                return self.__apiResponse(response, 400)
            self.__eventBus.safeInvoke(setMethod, data)
            return self.__apiResponse(data)

    def __apiConfig(self, name: str = None):
        return self.__apiServiceNamedDictionaryRequest(
            name, self.getConfig, self.setConfig)

    def __apiPrograms(self, name: str = None):
        return self.__apiServiceNamedDictionaryRequest(
            name, self.getPrograms, self.setPrograms)

    def __apiSchedules(self, name: str = None):
        return self.__apiServiceNamedDictionaryRequest(
            name, self.getSchedules, self.setSchedules)

    def __apiActions(self, name: str = None):
        actions = ['nextMode', 'changeComfort']

        if 'GET' == request.method:
            return self.__apiResponse(actions)

        if 'POST' == request.method:
            if name not in actions:
                return self.__apiResponse("Unsupport action", 400)
            if 'nextMode' == name:
                self.__eventBus.safeInvoke(self.nextMode)
            elif 'changeComfort' == name:
                offset = float(request.args.get('offset', 0.0))
                value = float(request.args.get('value', -1.0))
                self.__eventBus.safeInvoke(
                    self.modifyComfortSettings, offset=offset, value=value)
            return self.__apiStatus()

    def __apiActionNextMode(self):
        self.__eventBus.safeInvoke(self.nextMode)
        return self.__apiStatus()

    def __apiActionChangeComfort(self):
        offset = float(request.args.get('offset', 0.0))
        value = float(request.args.get('value', -1.0))
        self.__eventBus.safeInvoke(
            self.modifyComfortSettings, offset=offset, value=value)
        return self.__apiStatus()

    @ require_appkey
    def __apiActionStop(self):
        VALID_API_KEYS.remove(self.__sessionApiKey)
        data = self.__eventBus.safeInvoke(self.getStatus)
        response = self.__apiResponse(data)
        self.__eventBus.stop()
        return response

    def __flaskEntryPoint(self):
        try:
            self.__app.run("0.0.0.0", 5000)
            log.error("Somehow we exited the Flask thread")
        except:
            handleException("starting flask")
