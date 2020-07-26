from time import localtime
from sqlalchemy import desc

from .RelayManagementService import RelayManagementService
from .OrmManagementService import OrmManagementService
from src.logging import log
from src.core import EventBus, ServiceConsumer, ServiceProvider, \
    ThermostatState, ThermostatMode
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, UserThermostatInteractionEvent, \
    ThermostatStateChangingEvent, PowerPriceChangedEvent, \
    SettingsChangedEvent
from src.core.orm import OrmScheduleDay, OrmPriceOverride


class ThermostatService(ServiceConsumer):

    def __init__(self):
        self.__lastOverridePrice = None
        self.__isInPriceOverride = False
        self.__priceWindowHistory = []
        self.__priceWindow = None

        self.__currentProgramName = None
        self.__comfortMin = 68.0
        self.__comfortMax = 78.0
        self.__state = ThermostatState.OFF
        self.__mode = ThermostatMode.OFF

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        ormManagementService = self._getService(OrmManagementService)
        self.__delta = ormManagementService.getConfigFloat(
            'thermostat.delta')
        self.__fanRunoutDuration = ormManagementService.getConfigInt(
            'thermostat.fanRunoutDuration')

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
        eventBus.installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)

        self.__checkSchedule()

    @property
    def currentProgramName(self):
        return self.__currentProgramName

    @property
    def isInPriceOverride(self):
        return self.__isInPriceOverride

    @property
    def state(self):
        """ Current state of the thermostat """
        return self.__state

    @property
    def comfortMin(self):
        """ Minimum temperature that is comfortable, anything lower
        and outside the delta needs the thermostat to heat
        """
        return self.__comfortMin

    @comfortMin.setter
    def comfortMin(self, value):
        eventBus = self._getService(EventBus)
        self.__comfortMin = value
        self.__comfortMax = max(
            self.__comfortMax, self.__comfortMin + 2 * self.__delta)
        eventBus.fireEvent(SettingsChangedEvent())

    @property
    def comfortMax(self):
        """ Maximum temperature that is comfortable, anything higher
        and outside the delta needs the thermostat to cool
        """
        return self.__comfortMax

    @comfortMax.setter
    def comfortMax(self, value):
        eventBus = self._getService(EventBus)
        self.__comfortMax = value
        self.__comfortMin = min(
            self.__comfortMin, self.__comfortMax - 2 * self.__delta)
        eventBus.fireEvent(SettingsChangedEvent())

    @property
    def mode(self):
        """ The current mode the thermostat is in """
        return self.__mode

    @mode.setter
    def mode(self, value):
        eventBus = self._getService(EventBus)
        self.__mode = value
        eventBus.fireEvent(SettingsChangedEvent())

    def __checkSchedule(self):
        ''' Every so often, thermostat should re-check the database and see
        whether a new program is applicable '''
        ormManagementService = self._getService(OrmManagementService)
        eventBus = self._getService(EventBus)

        # Get the entire set of days and times so we can look across the
        # entire weekly schedule
        scheduleTimesList = list()
        for scheduleDay in ormManagementService.session.query(OrmScheduleDay):
            for scheduleTime in scheduleDay.schedule.times:
                timeInMinutes = scheduleTime.minute + 60 * \
                    (scheduleTime.hour + 24*scheduleDay.day)
                scheduleTime = scheduleTime
                scheduleTimesList.append((timeInMinutes, scheduleTime))

        if len(scheduleTimesList):
            # Now order the list in day/hour/minute order but in reverse so
            # we can apply 'now > instance' logic, then search the list...
            scheduleTimesList.sort(key=lambda a: a[0])
            scheduleTimesList.reverse()

            # If we match nothing below, then assume we carry in the
            # configured schedule from the last entry from last week
            currentScheduleTime = scheduleTimesList[0][1]
            timeData = localtime(eventBus.now)
            now = timeData.tm_min + 60*(timeData.tm_hour + 24*timeData.tm_wday)
            for entry in scheduleTimesList:
                if now > entry[0]:
                    currentScheduleTime = entry[1]
                    break

            if self.__currentProgramName != currentScheduleTime.program_name:
                self.__currentProgramName = currentScheduleTime.program_name
                self.__comfortMin = currentScheduleTime.program.comfort_min
                self.__comfortMax = currentScheduleTime.program.comfort_max
                eventBus.fireEvent(SettingsChangedEvent())

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        """ Based on a new power price searches the price overrides to
        determine whether the min/max values need updating and if so,
        applies the new settings.  Returs True if new settings were applied,
        False otherwise """
        ormManagementService = self._getService(OrmManagementService)
        eventBus = self._getService(EventBus)

        # Here we're simply assuming that price average resets every 15
        # minutes.  In production we'll get an update roughly every 5
        # minutes and the average of the three is the correct price to
        # use when looking up an override value
        priceWindow = int(eventBus.now/900)
        if self.__priceWindow != priceWindow:
            self.__priceWindow = priceWindow
            self.__priceWindowHistory = list()

        self.__priceWindowHistory.append(event.price)
        priceHistoryLength = len(self.__priceWindowHistory)
        priceAverage = sum(self.__priceWindowHistory)/priceHistoryLength

        if self.__currentProgramName is not None:
            priceOverrides = \
                ormManagementService.session.query(OrmPriceOverride). \
                filter_by(program_name=self.__currentProgramName). \
                order_by(desc(OrmPriceOverride.price))
            for priceOverride in priceOverrides:
                if priceAverage >= priceOverride.price:
                    if self.__lastOverridePrice != priceOverride.price:
                        self.__lastOverridePrice = priceOverride.price
                        self.__isInPriceOverride = True
                        if priceOverride.comfort_min is not None:
                            self.__comfortMin = priceOverride.comfort_min
                        if priceOverride.comfort_max is not None:
                            self.__comfortMax = priceOverride.comfort_max
                        eventBus.fireEvent(SettingsChangedEvent())
                    return

            if self.__lastOverridePrice is not None:
                self.__lastOverridePrice = None
                self.__isInPriceOverride = False
                self.__currentProgramName = None
                self.__checkSchedule()

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        temperature = event.temperature

        #    HEATING ZONE          COMFORT ZONE          COOLING ZONE
        # \\\\\\\\\\\\\\\\\\\                        ///////////////////
        # --------(----+----)------------------------(----+----)--------
        #        h1    H    h2                      c2    C    c1
        c1 = self.__comfortMax + self.__delta
        c2 = self.__comfortMax - self.__delta
        h2 = self.__comfortMin + self.__delta
        h1 = self.__comfortMin - self.__delta

        modeOff = ThermostatMode.OFF == self.__mode
        modeFan = ThermostatMode.FAN == self.__mode
        modeHeat = ThermostatMode.HEAT == self.__mode
        modeCool = ThermostatMode.COOL == self.__mode
        modeAuto = ThermostatMode.AUTO == self.__mode
        couldHeat = modeAuto or modeHeat
        couldCool = modeAuto or modeCool

        if ThermostatState.OFF == self.__state:
            if couldHeat and temperature < h1:
                self.__changeState(ThermostatState.HEATING)
            elif couldCool and temperature > c1:
                self.__changeState(ThermostatState.COOLING)
            elif ThermostatMode.FAN == self.__mode:
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

    def __changeState(self, newState: ThermostatState):
        eventBus = self._getService(EventBus)
        if self.__state != newState:
            event = ThermostatStateChangingEvent(newState)
            eventBus.fireEvent(event, immediately=True)

            relayManagementService = \
                self._getService(RelayManagementService)

            relayManagementService.openRelay(self.__state)
            if newState.shouldAlsoRunFan:
                log.debug(f"State from {self.__state} -> ThermostatState.FAN")
                relayManagementService.closeRelay(ThermostatState.FAN)
            log.debug(f"State from {self.__state} -> {newState}")
            relayManagementService.closeRelay(newState)
            self.__state = newState
            eventBus.fireEvent(ThermostatStateChangedEvent(newState))

    def __userThermostatInteraction(
            self, event: UserThermostatInteractionEvent):
        if event.interaction == UserThermostatInteractionEvent.MODE_NEXT:
            self.mode = ThermostatMode(
                (int(self.__mode.value) + 1) % len(ThermostatMode))
        if event.interaction == UserThermostatInteractionEvent.COMFORT_LOWER:
            self._modifyComfortSettings(-1)
        if event.interaction == UserThermostatInteractionEvent.COMFORT_RAISE:
            self._modifyComfortSettings(1)

    def _modifyComfortSettings(self, increment: int):
        if ThermostatMode.HEAT == self.__mode:
            self.comfortMin += increment
        elif ThermostatMode.COOL == self.__mode:
            self.comfortMax += increment

    def __fanRunout(self):
        if self.__state == ThermostatState.FAN and \
                self.__mode != ThermostatMode.FAN:
            self.__changeState(ThermostatState.OFF)
