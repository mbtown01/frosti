# pylint: disable=import-error
import RPi.GPIO as GPIO
# pylint: enable=import-error

from enum import Enum

from .HD44780Display import HD44780Display
from .Bme280EnvironmentSensor import Bme280EnvironmentSensor
from .PanasonicAgqRelay import PanasonicAgqRelay
from src.core.generics import GenericEnvironmentSensor
from src.core import Event, ThermostatState, ServiceProvider
from src.services import ThermostatService


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


class HardwareThermostatService_v2(ThermostatService):

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        sensor = Bme280EnvironmentSensor()

        super().__init__(
            lcd=HD44780Display(0x27, 20, 4),
            sensor=sensor,
            relays=(
                PanasonicAgqRelay(ThermostatState.FAN, 12, 6),  # 12 grounds
                PanasonicAgqRelay(ThermostatState.HEATING, 21, 20),
                PanasonicAgqRelay(ThermostatState.COOLING, 16, 19)
            )
        )

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        self._installEventHandler(
            ButtonPressedEvent, self.__buttonPressedHandler)

        self.__pinToButtonMap = {}
        self.__subscribeToButton(17, Button.UP)
        self.__subscribeToButton(18, Button.DOWN)
        self.__subscribeToButton(22, Button.MODE)
        self.__subscribeToButton(27, Button.WAKE)

    def __buttonPressedHandler(self, event: ButtonPressedEvent):
        if event.button == Button.UP:
            super()._modifyComfortSettings(1)
        elif event.button == Button.DOWN:
            super()._modifyComfortSettings(-1)
        elif event.button == Button.MODE:
            super()._nextMode()

    def __subscribeToButton(self, pin: int, button: Button):
        self.__pinToButtonMap[pin] = button

        GPIO.setup(
            pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(
            pin, GPIO.RISING, callback=self.__buttonCallback, bouncetime=200)

    def __buttonCallback(self, channel):
        """ Callback happens on another thread, so this method is marshaling
        ButtonPressedEvent instances to the main thread to handle """
        if not super().relayToggled:
            button = self.__pinToButtonMap[channel]
            self._fireEvent(ButtonPressedEvent(button))
