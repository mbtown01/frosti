from src.logging import log
from src.services import SettingsService, SettingsChangedEvent
from src.core import EventBusMember, ServiceProvider, ThermostatState
from src.services import ConfigService
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent
from src.core.generics import GenericLcdDisplay, GenericRgbLed


class GenericUserInterface(EventBusMember):

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
        self.__redrawAndRotateInvoker = self._installTimerHandler(
            frequency=3.0, handlers=self.__redrawAndRotate)
        self.__rowTwoOffset = 0
        self.__rowTwoEntries = [
            "Target:             ", "State:              ",
            "Price:              ", "Program:            ",
        ]

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
            SettingsChangedEvent, self.__settingsChanged)
        self._installEventHandler(
            SensorDataChangedEvent, self.__sensorDataChanged)
        self._installEventHandler(
            ThermostatStateChangedEvent, self.__stateChanged)
        self._installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)

        self.__lcd.setBacklight(True)

    def __priceOverrideAnimate(self):
        index = self.__priceOverrideColorIndex
        listSize = len(self.__priceOverrideColorList)
        for rgbLed in self.__rgbLeds:
            rgbLed.setColor(self.__priceOverrideColorList[index])
            index = (index+1) % listSize
        self.__priceOverrideColorIndex = \
            (self.__priceOverrideColorIndex+1) % listSize

    def backlightReset(self):
        if not self.__backlightTimeoutInvoker.isQueued:
            self.__lcd.setBacklight(True)
            self.__lcd.commit()
        self.__backlightTimeoutInvoker.reset()

    def __backlightTimeout(self):
        self.__lcd.setBacklight(False)

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.redraw()

    def __settingsChanged(self, event: SettingsChangedEvent):
        settings = self._getService(SettingsService)
        if settings.isInPriceOverride:
            self.__priceOverrideAnimateInvoker.reset()
        else:
            self.__priceOverrideAnimateInvoker.disable()
            for rgbLed in self.__rgbLeds:
                rgbLed.setColor(GenericRgbLed.Color.BLACK)

        heat = settings.comfortMin
        cool = settings.comfortMax
        name = settings.currentProgram.name
        mode = str(settings.mode).replace('Mode.', '')
        log.debug(f"[{name}] mode={mode} {heat:<3.0f}/{cool:>3.0f}")

        self.__rowTwoEntries[0] = f'Target:      {heat:<3.0f}/{cool:>3.0f}'
        self.__rowTwoEntries[3] = f'Program: {name:>11s}'
        self.__rowTwoOffset = 0
        self.__redrawAndRotateInvoker.reset()
        self.redraw()

    def __stateChanged(self, event: ThermostatStateChangedEvent):
        state = str(event.state).replace('ThermostatState.', '')
        self.__rowTwoEntries[1] = f'State: {state:>13s}'
        self.__rowTwoOffset = 1
        self.__redrawAndRotateInvoker.reset()
        self.redraw()

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        self.__rowTwoEntries[2] = f'Price:  ${event.price:.4f}/kW*h'
        self.__rowTwoOffset = 2
        self.__redrawAndRotateInvoker.reset()
        self.redraw()

    def __redrawAndRotate(self):
        self.redraw()
        self.__rowTwoOffset = (self.__rowTwoOffset + 1) % \
            len(self.__rowTwoEntries)

    def redraw(self):
        settings = self._getService(SettingsService)

        now = self.__lastTemperature
        mode = str(settings.mode).replace('Mode.', '')
        self.__lcd.update(0, 0, f'Now: {now:<5.1f}    {mode:>6s}')
        self.__lcd.update(1, 0, self.__rowTwoEntries[self.__rowTwoOffset])
        self.__lcd.update(3, 0, r'UP  DOWN  MODE  NEXT')
        self.__lcd.commit()
