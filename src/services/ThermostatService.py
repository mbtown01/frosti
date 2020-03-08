from enum import Enum
from time import time, localtime
import atexit

from src.logging import log
from src.services import SettingsService, SettingsChangedEvent
from src.core import EventBus, EventBusMember, Event, TimerBasedHandler, \
    ServiceProvider, ThermostatState
from src.services import ConfigService
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent, \
    UserThermostatInteractionEvent
from src.core.generics import GenericEnvironmentSensor, GenericLcdDisplay, \
    GenericRelay


class ThermostatService(EventBusMember):

    def __init__(self,
                 lcd: GenericLcdDisplay,
                 sensor: GenericEnvironmentSensor,
                 relays: list):
        self.__lcd = lcd
        self.__sensor = sensor
        self.__relayToggled = False
        self.__relayMap = {r.function: r for r in relays}
        for relay in relays:
            relay.addCallback(self.__relayCallback)
        if ThermostatState.OFF not in self.__relayMap:
            self.__relayMap[ThermostatState.OFF] = \
                GenericRelay(ThermostatState.OFF)
        self.__state = ThermostatState.OFF
        self.__lcd.setBacklight(True)
        self.__lastTemperature = 0.0
        self.__lastState = ThermostatState.OFF
        self.__lastPrice = 0.0
        self.__fanRunoutInvoker = None

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(ConfigService)
        self.__delta = \
            config.value('thermostat').value('delta', 1.0)
        self.__fanRunoutDuration = \
            config.value('thermostat').value('fanRunout', 30)
        self.__backlightTimeoutDuration = \
            config.value('thermostat').value('backlightTimeout', 10)

        self.__sampleSensorsInvoker = self._installTimerHandler(
            frequency=5.0,
            handlers=self.__sampleSensors)
        self.__checkScheduleInvoker = self._installTimerHandler(
            frequency=60.0,
            handlers=self.__checkSchedule)
        self.__backlightTimeoutInvoker = self._installTimerHandler(
            frequency=self.__backlightTimeoutDuration,
            handlers=self.__backlightTimeout,
            oneShot=True)
        self.__relayToggledTimeoutInvoker = self._installTimerHandler(
            frequency=3.0, handlers=self.__relayToggledTimeout,
            oneShot=True)
        self.__drawRowTwoInvoker = self._installTimerHandler(
            frequency=3.0,
            handlers=[
                self.__drawRowTwoTarget,
                self.__drawRowTwoState,
                self.__drawRowTwoPrice,
                self.__drawRowTwoProgram])
        self.__fanRunoutInvoker = self._installTimerHandler(
            frequency=self.__fanRunoutDuration,
            handlers=self.__fanRunout,
            oneShot=True)
        self.__fanRunoutInvoker.disable()

        self._installEventHandler(
            SettingsChangedEvent, self.__processSettingsChanged)
        self._installEventHandler(
            SensorDataChangedEvent, self.__processSensorDataChanged)
        self._installEventHandler(
            ThermostatStateChangedEvent, self.__processStateChanged)
        self._installEventHandler(
            PowerPriceChangedEvent, self._powerPriceChanged)
        self._installEventHandler(
            UserThermostatInteractionEvent, self.__userThermostatInteraction)

        self.__lcd.setBacklight(True)
        self.__openAllRelays()
        self.__checkSchedule()

    @property
    def state(self):
        """ Current state of the thermostat """
        return self.__state

    @property
    def relayToggled(self):
        return self.__relayToggled

    def __checkSchedule(self):
        settings = self._getService(SettingsService)
        eventBus = self._getService(EventBus)

        if eventBus.now is None:
            raise RuntimeError("No time on eventBus")
        values = localtime(eventBus.now)
        settings.timeChanged(
            day=values.tm_wday, hour=values.tm_hour, minute=values.tm_min)
        # self.__sampleSensors()

    def __sampleSensors(self):
        temperature = self.__sensor.temperature
        settings = self._getService(SettingsService)
        super()._fireEvent(SensorDataChangedEvent(
            temperature=temperature,
            pressure=self.__sensor.pressure,
            humidity=self.__sensor.humidity
        ))

        #    HEATING ZONE         COMFORT ZONE           COOLING ZONE
        # \\\\\\\\\\\\\\\\\\\                        ///////////////////
        # --------(----+----)------------------------(----+----)--------
        #        h1    H    h2                      c2    C    c1
        c1 = settings.comfortMax+self.__delta
        c2 = settings.comfortMax-self.__delta
        h2 = settings.comfortMin+self.__delta
        h1 = settings.comfortMin-self.__delta

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

        self.__backlightReset()
        if SettingsService.Mode.HEAT == settings.mode:
            settings.comfortMin = settings.comfortMin + increment
        if SettingsService.Mode.COOL == settings.mode:
            settings.comfortMax = settings.comfortMax + increment
        self.__sampleSensorsInvoker.reset()

    def _nextMode(self):
        settings = self._getService(SettingsService)

        self.__backlightReset()
        settings.mode = SettingsService.Mode(
            (int(settings.mode.value)+1) % len(SettingsService.Mode))
        self.__sampleSensorsInvoker.reset()

    def __changeState(self, newState: ThermostatState):
        if self.__state != newState:
            log.debug(f"Thermostat state {self.__state} -> {newState}")
            self.__relayMap[self.__state].openRelay()
            self.__relayMap[newState].closeRelay()
            if newState.shouldAlsoRunFan:
                self.__relayMap[ThermostatState.FAN].closeRelay()
            self.__state = newState
            self._fireEvent(ThermostatStateChangedEvent(newState))

    def __relayCallback(self, relay: GenericRelay):
        self.__relayToggled = True
        self.__relayToggledTimeoutInvoker.reset()
        log.debug("Driver ENTERING relay toggle timeout")

    def __relayToggledTimeout(self):
        self.__relayToggled = False
        log.debug("Driver COMPLETED relay toggle timeout")

    def __fanRunout(self):
        settings = self._getService(SettingsService)

        if self.__state == ThermostatState.FAN and \
                settings.mode != SettingsService.Mode.FAN:
            self.__changeState(ThermostatState.OFF)

    def __backlightReset(self):
        if not self.__backlightTimeoutInvoker.isQueued:
            self.__lcd.setBacklight(True)
            self.__lcd.commit()
        self.__backlightTimeoutInvoker.reset()

    def __backlightTimeout(self):
        self.__lcd.setBacklight(False)

    def __openAllRelays(self):
        for relay in self.__relayMap.values():
            relay.openRelay()

    def _powerPriceChanged(self, event: PowerPriceChangedEvent):
        settings = self._getService(SettingsService)

        settings.priceChanged(event.price)
        self.__lastPrice = event.price
        self.__drawRowTwoInvoker.reset(2)
        self.__drawRowTwoInvoker.invokeCurrent()

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        settings = self._getService(SettingsService)
        log.debug(f"New settings: {settings}")
        self.__drawLcdDisplay()
        self.__drawRowTwoInvoker.reset(0)
        self.__drawRowTwoInvoker.invokeCurrent()

    def __processStateChanged(self, event: ThermostatStateChangedEvent):
        self.__lastState = event.state
        self.__drawLcdDisplay()
        self.__drawRowTwoInvoker.reset(1)
        self.__drawRowTwoInvoker.invokeCurrent()

    def __processSensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.__drawLcdDisplay()

    def __drawRowTwoTarget(self):
        settings = self._getService(SettingsService)

        heat = settings.comfortMin
        cool = settings.comfortMax
        self.__lcd.update(1, 0, f'Target:      {heat:<3.0f}/{cool:>3.0f}')
        self.__lcd.commit()

    def __drawRowTwoState(self):
        state = str(self.__lastState).replace('ThermostatState.', '')
        self.__lcd.update(1, 0, f'State:{state:>14s}')
        self.__lcd.commit()

    def __drawRowTwoPrice(self):
        price = self.__lastPrice
        self.__lcd.update(1, 0, f'Price:  ${price:.4f}/kW*h')
        self.__lcd.commit()

    def __drawRowTwoProgram(self):
        settings = self._getService(SettingsService)
        name = settings.currentProgram.name
        self.__lcd.update(1, 0, f'Program: {name:>11s}')
        self.__lcd.commit()

    def __drawLcdDisplay(self):
        settings = self._getService(SettingsService)

        now = self.__lastTemperature
        mode = str(settings.mode).replace('Mode.', '')
        self.__lcd.update(0, 0, f'Now: {now:<5.1f}    {mode:>6s}')
        self.__lcd.update(3, 0, r'UP  DOWN  MODE  NEXT')
        self.__lcd.commit()
