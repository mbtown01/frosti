from .ThermostatService import ThermostatService
from .OrmManagementService import OrmManagementService
from frosti.core import ServiceProvider, ServiceConsumer, EventBus, \
    ThermostatState, ThermostatMode
from frosti.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent, SettingsChangedEvent
from frosti.core.orm import OrmSensorReading, OrmThermostatState, \
    OrmThermostatTargets, OrmGriddyUpdate


class OrmStateCaptureService(ServiceConsumer):
    MODE_CODES = {
        ThermostatMode.OFF: 0x00,
        ThermostatMode.FAN: 0x01,
        ThermostatMode.HEAT: 0x03,
        ThermostatMode.COOL: 0x05,
        ThermostatMode.AUTO: 0x07
    }

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        eventBus = self._getService(EventBus)
        eventBus.installEventHandler(
            SensorDataChangedEvent, self.__sensorDataChanged)
        eventBus.installEventHandler(
            ThermostatStateChangedEvent, self.__thermostatStateChanged)
        eventBus.installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)
        eventBus.installEventHandler(
            SettingsChangedEvent, self.__processSettingsChanged)

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        ormManagementService = self._getService(OrmManagementService)

        entity = OrmGriddyUpdate()
        entity.price = event.price

        ormManagementService.session.add(entity)
        ormManagementService.session.commit()

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        ormManagementService = self._getService(OrmManagementService)
        thermostatService = self._getService(ThermostatService)

        entity = OrmThermostatTargets()
        entity.mode = self.MODE_CODES[thermostatService.mode]
        entity.comfort_max = thermostatService.comfortMax
        entity.comfort_min = thermostatService.comfortMin

        ormManagementService.session.add(entity)
        ormManagementService.session.commit()

    def __thermostatStateChanged(self, event: ThermostatStateChangedEvent):
        ormManagementService = self._getService(OrmManagementService)

        entity = OrmThermostatState()
        entity.cooling = 1 if ThermostatState.COOLING == event.state else 0
        entity.heating = 1 if ThermostatState.HEATING == event.state else 0
        entity.fan = 1 if ThermostatState.FAN == event.state else 0

        ormManagementService.session.add(entity)
        ormManagementService.session.commit()

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        ormManagementService = self._getService(OrmManagementService)

        entity = OrmSensorReading()
        entity.temperature = event.temperature
        entity.pressure = event.pressure
        entity.humidity = event.humidity

        ormManagementService.session.add(entity)
        ormManagementService.session.commit()
