from enum import Enum

from .GenericLcdDisplay import GenericLcdDisplay
from .GenericRgbLed import GenericRgbLed
from src.logging import log
from src.services import SettingsService, SettingsChangedEvent
from src.core import ServiceConsumer, ServiceProvider, EventBus, Event
from src.services import ConfigService, ThermostatService
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent, \
    UserThermostatInteractionEvent


class GenericUserInterface(ServiceConsumer):

    class Button(Enum):
        UP = 1
        DOWN = 2
        MODE = 3
        WAKE = 4

    class ButtonPressedEvent(Event):
        def __init__(self, button):
            super().__init__(data={'button': button})

        @property
        def button(self):
            return super().data['button']

    def __init__(self,
                 lcd: GenericLcdDisplay,
                 rgbLeds: list=[]):
        self.__lcd = lcd
        self.__rgbLeds = rgbLeds
        self.__lcd.setBacklight(True)
        self.__lastTemperature = 0.0
        self.__rowTwoOffset = 0
        self.__ledColorIndex = 0

        self.__rowTwoEntries = [
            "Target:             ",
            "State:              ",
            "Price:              ",
            "Program:            ",
        ]

        self.__ledColorList = []

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(ConfigService)
        self.__backlightTimeoutDuration = \
            config.value('thermostat').value('backlightTimeout', 10)

        eventBus = self._getService(EventBus)
        self.__backlightTimeoutInvoker = eventBus.installTimer(
            frequency=self.__backlightTimeoutDuration,
            handler=self.__backlightTimeout, oneShot=True)
        self.__redrawAndRotateInvoker = eventBus.installTimer(
            frequency=5.0, handler=self.__redrawAndRotate)
        self.__ledAnimateInvoker = eventBus.installTimer(
            frequency=0.5, handler=self.__ledAnimate)
        self.__ledAnimateInvoker.disable()

        eventBus.installEventHandler(
            SettingsChangedEvent, self.__settingsChanged)
        eventBus.installEventHandler(
            SensorDataChangedEvent, self.__sensorDataChanged)
        eventBus.installEventHandler(
            ThermostatStateChangedEvent, self.__stateChanged)
        eventBus.installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)
        eventBus.installEventHandler(
            GenericUserInterface.ButtonPressedEvent,
            self.__buttonPressedHandler)

        thermostat = self._getService(ThermostatService)
        self.__stateChanged(ThermostatStateChangedEvent(thermostat.state))

        self.__lcd.setBacklight(True)

    def backlightReset(self):
        if not self.__backlightTimeoutInvoker.isQueued:
            self.__lcd.setBacklight(True)
            self.__lcd.commit()
        self.__backlightTimeoutInvoker.reset()

    def __ledAnimate(self):
        listSize = len(self.__ledColorList)
        for rgbLed in self.__rgbLeds:
            rgbLed.setColor(self.__ledColorList[self.__ledColorIndex])
            # index = (index+1) % listSize
        self.__ledColorIndex = \
            (self.__ledColorIndex + 1) % listSize

    def __backlightTimeout(self):
        self.__lcd.setBacklight(False)

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.redraw()

    def __buttonPressedHandler(self, event: ButtonPressedEvent):
        self.backlightReset()
        eventBus = self._getService(EventBus)

        if event.button == GenericUserInterface.Button.UP:
            eventBus.fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.COMFORT_RAISE))
        elif event.button == GenericUserInterface.Button.DOWN:
            eventBus.fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.COMFORT_LOWER))
        elif event.button == GenericUserInterface.Button.MODE:
            eventBus.fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.MODE_NEXT))
        elif event.button == GenericUserInterface.Button.WAKE:
            self.__lcd.hardReset()
            self.__lcd.clear()
            super().redraw()

    def __settingsChanged(self, event: SettingsChangedEvent):
        settings = self._getService(SettingsService)
        if settings.isInPriceOverride:
            self.__ledColorList = [
                GenericRgbLed.Color.BLUE,
                GenericRgbLed.Color.CYAN,
                GenericRgbLed.Color.GREEN,
                GenericRgbLed.Color.YELLOW,
                GenericRgbLed.Color.RED,
                GenericRgbLed.Color.MAGENTA,
            ]
            self.__ledAnimateInvoker.reset()
        else:
            self.__ledAnimateInvoker.disable()
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
