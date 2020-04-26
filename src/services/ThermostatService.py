from time import localtime

from .ConfigService import ConfigService
from .RelayManagementService import RelayManagementService
from .SettingsService import SettingsService
from src.logging import log
from src.core import EventBus, ServiceConsumer, ServiceProvider, \
    ThermostatState
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, UserThermostatInteractionEvent


class ThermostatService(ServiceConsumer):

    def __init__(self):
        self.__state = ThermostatState.OFF
        self.__fanRunoutInvoker = None

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(ConfigService)
        self.__delta = \
            config.value('thermostat').value('delta', 1.0)
        self.__fanRunoutDuration = \
            config.value('thermostat').value('fanRunout', 30)

        eventBus = self._getService(EventBus)
        self.__checkScheduleInvoker = eventBus.installTimer(
            frequency=60.0, handler=self.__checkSchedule)
        self.__fanRunoutInvoker = eventBus.installTimer(
            frequency=self.__fanRunoutDuration, handler=self.__fanRunout,
            oneShot=True)
        self.__fanRunoutInvoker.disable()

        eventBus.installEventHandler(
            UserThermostatInteractionEvent, self.__userThermostatInteraction)
        eventBus.installEventHandler(
            SensorDataChangedEvent, self.__sensorDataChanged)

        self.__checkSchedule()

    @property
    def state(self):
        """ Current state of the thermostat """
        return self.__state

    def __checkSchedule(self):
        settings = self._getService(SettingsService)
        eventBus = self._getService(EventBus)

        if eventBus.now is None:
            raise RuntimeError("No time on eventBus")
        values = localtime(eventBus.now)
        settings.timeChanged(
            day=values.tm_wday, hour=values.tm_hour, minute=values.tm_min)

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        temperature = event.temperature
        settings = self._getService(SettingsService)

        #    HEATING ZONE         COMFORT ZONE           COOLING ZONE
        # \\\\\\\\\\\\\\\\\\\                        ///////////////////
        # --------(----+----)------------------------(----+----)--------
        #        h1    H    h2                      c2    C    c1
        c1 = settings.comfortMax + self.__delta
        c2 = settings.comfortMax - self.__delta
        h2 = settings.comfortMin + self.__delta
        h1 = settings.comfortMin - self.__delta

        modeOff = SettingsService.Mode.OFF == settings.mode
        modeFan = SettingsService.Mode.FAN == settings.mode
        modeHeat = SettingsService.Mode.HEAT == settings.mode
        modeCool = SettingsService.Mode.COOL == settings.mode
        modeAuto = SettingsService.Mode.AUTO == settings.mode
        couldHeat = modeAuto or modeHeat
        couldCool = modeAuto or modeCool

        if ThermostatState.OFF == self.__state:
            if couldHeat and temperature < h1:
                self.__changeState(ThermostatState.HEATING)
            elif couldCool and temperature > c1:
                self.__changeState(ThermostatState.COOLING)
            elif SettingsService.Mode.FAN == settings.mode:
                self.__changeState(ThermostatState.FAN)
        elif ThermostatState.HEATING == self.__state:
            if modeAuto and temperature > c1:
                self.__changeState(ThermostatState.COOLING)
            elif modeFan:
                self.__changeState(ThermostatState.FAN)
            elif modeOff:
                self.__changeState(ThermostatState.FAN)
                self.__fanRunoutInvoker.reset()
            elif (couldHeat and temperature > h2):
                self.__changeState(ThermostatState.FAN)
                self.__fanRunoutInvoker.reset()
            elif modeCool:
                if temperature > c1:
                    self.__changeState(ThermostatState.COOLING)
                else:
                    self.__changeState(ThermostatState.FAN)
                    self.__fanRunoutInvoker.reset()
        elif ThermostatState.COOLING == self.__state:
            if modeAuto and temperature < h1:
                self.__changeState(ThermostatState.HEATING)
            elif modeFan:
                self.__changeState(ThermostatState.FAN)
            elif modeOff:
                self.__changeState(ThermostatState.FAN)
                self.__fanRunoutInvoker.reset()
            elif (couldCool and temperature < c2):
                self.__changeState(ThermostatState.FAN)
                self.__fanRunoutInvoker.reset()
            elif modeHeat:
                if temperature < h1:
                    self.__changeState(ThermostatState.HEATING)
                else:
                    self.__changeState(ThermostatState.FAN)
                    self.__fanRunoutInvoker.reset()
        elif ThermostatState.FAN == self.__state:
            if couldHeat and temperature < h1:
                self.__changeState(ThermostatState.HEATING)
            elif couldCool and temperature > c1:
                self.__changeState(ThermostatState.COOLING)
            elif modeOff and not self.__fanRunoutInvoker.isQueued:
                self.__changeState(ThermostatState.OFF)
        else:
            raise RuntimeError(f"Encountered unknown state {self.__state}")

    def __userThermostatInteraction(
            self, event: UserThermostatInteractionEvent):
        if event.interaction == UserThermostatInteractionEvent.MODE_NEXT:
            self._nextMode()
        if event.interaction == UserThermostatInteractionEvent.COMFORT_LOWER:
            self._modifyComfortSettings(-1)
        if event.interaction == UserThermostatInteractionEvent.COMFORT_RAISE:
            self._modifyComfortSettings(1)

    def _modifyComfortSettings(self, increment: int):
        settings = self._getService(SettingsService)

        if SettingsService.Mode.HEAT == settings.mode:
            settings.comfortMin = settings.comfortMin + increment
        if SettingsService.Mode.COOL == settings.mode:
            settings.comfortMax = settings.comfortMax + increment

    def _nextMode(self):
        settings = self._getService(SettingsService)

        settings.mode = SettingsService.Mode(
            (int(settings.mode.value) + 1) % len(SettingsService.Mode))

    def __changeState(self, newState: ThermostatState):
        eventBus = self._getService(EventBus)
        if self.__state != newState:
            relayManagementService = \
                super()._getService(RelayManagementService)

            log.debug(f"Thermostat state {self.__state} -> {newState}")
            relayManagementService.openRelay(self.__state)
            relayManagementService.closeRelay(newState)
            if newState.shouldAlsoRunFan:
                relayManagementService.closeRelay(ThermostatState.FAN)
            self.__state = newState
            eventBus.fireEvent(ThermostatStateChangedEvent(newState))

    def __fanRunout(self):
        settings = self._getService(SettingsService)

        if self.__state == ThermostatState.FAN and \
                settings.mode != SettingsService.Mode.FAN:
            self.__changeState(ThermostatState.OFF)
