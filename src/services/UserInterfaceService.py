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
    GenericRelay, GenericRgbLed


class UserInterfaceService(EventBusMember):

    def __init__(self,
                 lcd: GenericLcdDisplay,
                 rgbLeds: list=[]):
        self.__lcd = lcd
        self.__rgbLeds = rgbLeds
        self.__lcd.setBacklight(True)
        self.__lastTemperature = 0.0
        self.__lastState = ThermostatState.OFF
        self.__lastPrice = 0.0

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(ConfigService)
        self.__backlightTimeoutDuration = \
            config.value('thermostat').value('backlightTimeout', 10)

        self.__backlightTimeoutInvoker = self._installTimerHandler(
            frequency=self.__backlightTimeoutDuration,
            handlers=self.__backlightTimeout, oneShot=True)
        self.__drawRowTwoInvoker = self._installTimerHandler(
            frequency=3.0,
            handlers=[
                self.__drawRowTwoTarget,
                self.__drawRowTwoState,
                self.__drawRowTwoPrice,
                self.__drawRowTwoProgram])
        self.__priceOverrideColorList = [
            GenericRgbLed.Color.BLUE,
            GenericRgbLed.Color.CYAN,
            GenericRgbLed.Color.GREEN,
            GenericRgbLed.Color.YELLOW,
            GenericRgbLed.Color.RED,
            GenericRgbLed.Color.MAGENTA,
        ]
        self.__priceOverrideColorIndex = 0
        self.__priceOverrideAnimateInvoker = self._installTimerHandler(
            frequency=0.5, handlers=self.__priceOverrideAnimate)
        self.__priceOverrideAnimateInvoker.disable()

        self._installEventHandler(
            SettingsChangedEvent, self.__processSettingsChanged)
        self._installEventHandler(
            SensorDataChangedEvent, self.__processSensorDataChanged)
        self._installEventHandler(
            ThermostatStateChangedEvent, self.__processStateChanged)
        self._installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)
        self._installEventHandler(
            UserThermostatInteractionEvent, self.__userThermostatInteraction)

        self.__lcd.setBacklight(True)

    def __priceOverrideAnimate(self):
        index = self.__priceOverrideColorIndex
        listSize = len(self.__priceOverrideColorList)
        for rgbLed in self.__rgbLeds:
            rgbLed.setColor(self.__priceOverrideColorList[index])
            index = (index+1) % listSize
        self.__priceOverrideColorIndex = \
            (self.__priceOverrideColorIndex+1) % listSize

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

    def _nextMode(self):
        settings = self._getService(SettingsService)

        self.__backlightReset()
        settings.mode = SettingsService.Mode(
            (int(settings.mode.value)+1) % len(SettingsService.Mode))

    def __backlightReset(self):
        if not self.__backlightTimeoutInvoker.isQueued:
            self.__lcd.setBacklight(True)
            self.__lcd.commit()
        self.__backlightTimeoutInvoker.reset()

    def __backlightTimeout(self):
        self.__lcd.setBacklight(False)

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        self.__lastPrice = event.price
        self.__drawRowTwoInvoker.reset(2)
        self.__drawRowTwoInvoker.invokeCurrent()

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        settings = self._getService(SettingsService)
        if settings.isInPriceOverride:
            self.__priceOverrideAnimateInvoker.reset()
        else:
            self.__priceOverrideAnimateInvoker.disable()
            for rgbLed in self.__rgbLeds:
                rgbLed.setColor(GenericRgbLed.Color.BLACK)

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
