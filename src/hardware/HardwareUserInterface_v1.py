# pylint: disable=import-error
import RPi.GPIO as GPIO
# pylint: enable=import-error

from enum import Enum

from .HD44780Display import HD44780Display
from src.core.events import UserThermostatInteractionEvent
from src.core import Event, ServiceProvider, EventBus
from src.services import ThermostatService
from src.core.generics import GenericUserInterface


class Button(Enum):
    UP = 1
    DOWN = 2
    MODE = 3
    WAKE = 4


class ButtonPressedEvent(Event):
    def __init__(self, button: Button):
        super().__init__(data={'button': button})

    @property
    def button(self):
        return super().data['button']


class HardwareUserInterface_v1(GenericUserInterface):

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        self.__lcd = HD44780Display(0x27, 20, 4)
        self.__rgbLeds = [] 
        super().__init__(lcd=self.__lcd, rgbLeds=self.__rgbLeds)

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        eventBus = self._getService(EventBus)
        eventBus.installEventHandler(
            ButtonPressedEvent, self.__buttonPressedHandler)

        self.__pinToButtonMap = {}
        self.__subscribeToButton(21, Button.UP)
        self.__subscribeToButton(20, Button.DOWN)
        self.__subscribeToButton(16, Button.MODE)
        self.__subscribeToButton(12, Button.WAKE)

    def __buttonPressedHandler(self, event: ButtonPressedEvent):
        super().backlightReset()
        eventBus = self._getService(EventBus)

        if event.button == Button.UP:
            eventBus.fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.COMFORT_RAISE))
        elif event.button == Button.DOWN:
            eventBus.fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.COMFORT_LOWER))
        elif event.button == Button.MODE:
            eventBus.fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.MODE_NEXT))
        elif event.button == Button.WAKE:
            self.__lcd.hardReset()
            self.__lcd.clear()
            super().redraw()

    def __subscribeToButton(self, pin: int, button: Button):
        self.__pinToButtonMap[pin] = button

        GPIO.setup(
            pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(
            pin, GPIO.RISING, callback=self.__buttonCallback, bouncetime=200)

    def __buttonCallback(self, channel):
        """ Callback happens on another thread, so this method is marshaling
        ButtonPressedEvent instances to the main thread to handle """
        eventBus = self._getService(EventBus)
        button = self.__pinToButtonMap[channel]
        eventBus.fireEvent(ButtonPressedEvent(button))
