# pylint: disable=import-error
import RPi.GPIO as GPIO
# pylint: enable=import-error

from .HD44780Display import HD44780Display
from src.core import ServiceProvider, EventBus
from src.core.generics import GenericUserInterface
from src.core.events import ThermostatStateChangingEvent, \
    ThermostatStateChangedEvent


class HardwareUserInterface_v1(GenericUserInterface):

    def __init__(self):
        self.__ignoreButtons = False
        self.__lcd = HD44780Display(0x27, 20, 4)
        self.__rgbLeds = []
        super().__init__(lcd=self.__lcd, rgbLeds=self.__rgbLeds)

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        # There's something about our 24V -> 5V transformer circuit and
        # how the voltage changes when the HVAC goes on and off that
        # causes 'edges' on the GPIO pins.  To get around it, we simply
        # catch the ThermostatStateChangingEvent and ignore *ALL* user
        # interactions until we receive the ThermostatStateChangedEvent
        eventBus = self._getService(EventBus)
        eventBus.installEventHandler(
            ThermostatStateChangingEvent, self.__thermostatStateChanging)
        eventBus.installEventHandler(
            ThermostatStateChangedEvent, self.__thermostatStateChanged)

        self.__pinToButtonMap = {}
        self.__subscribeToButton(21, GenericUserInterface.Button.UP)
        self.__subscribeToButton(20, GenericUserInterface.Button.DOWN)
        self.__subscribeToButton(16, GenericUserInterface.Button.MODE)
        self.__subscribeToButton(12, GenericUserInterface.Button.WAKE)

    def __thermostatStateChanging(self, event: ThermostatStateChangingEvent):
        self.__ignoreButtons = True

    def __thermostatStateChanged(self, event: ThermostatStateChangedEvent):
        self.__ignoreButtons = False

    def __subscribeToButton(
            self, pin: int, button: GenericUserInterface.Button):
        self.__pinToButtonMap[pin] = button

        GPIO.setup(
            pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(
            pin, GPIO.RISING, callback=self.__buttonCallback, bouncetime=200)

    def __buttonCallback(self, channel):
        """ Callback happens on another thread, so this method is marshaling
        ButtonPressedEvent instances to the main thread to handle """
        if not self.__ignoreButtons:
            eventBus = self._getService(EventBus)
            button = self.__pinToButtonMap[channel]
            eventBus.fireEvent(GenericUserInterface.ButtonPressedEvent(button))
