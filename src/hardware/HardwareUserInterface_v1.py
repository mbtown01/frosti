# pylint: disable=import-error
import RPi.GPIO as GPIO
# pylint: enable=import-error

from enum import Enum

from .HD44780Display import HD44780Display
from src.core import Event, ServiceProvider
from src.services import ThermostatService
from src.logging import log


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


class HardwareUserInterface_v1(ThermostatService):

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        super().__init__(lcd=HD44780Display(0x27, 20, 4))

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        self._installEventHandler(
            ButtonPressedEvent, self.__buttonPressedHandler)

        self.__pinToButtonMap = {}
        self.__subscribeToButton(21, Button.UP)
        self.__subscribeToButton(20, Button.DOWN)
        self.__subscribeToButton(16, Button.MODE)
        self.__subscribeToButton(12, Button.WAKE)

    def __buttonPressedHandler(self, event: ButtonPressedEvent):
        if event.button == Button.UP:
            self._fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.COMFORT_RAISE))
        elif event.button == Button.DOWN:
            self._fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.COMFORT_LOWER))
        elif event.button == Button.MODE:
            self._fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.MODE_NEXT))

    def __subscribeToButton(self, pin: int, button: Button):
        self.__pinToButtonMap[pin] = button

        GPIO.setup(
            pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(
            pin, GPIO.RISING, callback=self.__buttonCallback, bouncetime=200)

    def __buttonCallback(self, channel):
        """ Callback happens on another thread, so this method is marshaling
        ButtonPressedEvent instances to the main thread to handle """
        log.warning("Not currently filtering for recent relay activity")
        button = self.__pinToButtonMap[channel]
        self._fireEvent(ButtonPressedEvent(button))
