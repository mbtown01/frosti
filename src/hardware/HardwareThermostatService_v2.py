# pylint: disable=import-error
import RPi.GPIO as GPIO
import board
import busio
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017
# pylint: enable=import-error

from enum import Enum
from time import sleep

from .HD44780Display import HD44780Display
from .Bme280EnvironmentSensor import Bme280EnvironmentSensor
from .PanasonicAgqRelay import PanasonicAgqRelay
from src.core.generics import GenericEnvironmentSensor
from src.core import Event, ThermostatState, ServiceProvider
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


class HardwareThermostatService_v2(ThermostatService):

    def __foo(self, port):
        log.debug(f'Some kind of interrupt happened on port {port}')
        for p in range(0,16):
            v = self.__pins[p].value
            log.debug(f"   pin[{p}] = {v}")

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        i2c = busio.I2C(board.SCL, board.SDA)
        mcp = MCP23017(i2c)

        self.__pins = []
        for p in range(0, 16):
            pin = mcp.get_pin(p)
            pin.direction = Direction.INPUT
            pin.pull = Pull.UP
            self.__pins.append(pin)

        # Only docs for this I could find are at
        # https://github.com/adafruit/Adafruit_CircuitPython_MCP230xx/blob/master/examples/mcp230xx_event_detect_interrupt.py

        # GPINTEN controls interrupt-on-change feature per pin
        mcp.interrupt_enable = 0xFFFF  # Enable Interrupts in all pins
        # INTCON Interrupt control register
        mcp.interrupt_configuration = 0x0000
        # DEFVAL controls default comparison value
        mcp.default_value = 0xFFFF
        # Interrupt as open drain and mirrored
        mcp.io_control = 0x44

        mcp.clear_ints()  # Interrupts need to be cleared initially

        GPIO.setup(17, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(
            17, GPIO.FALLING, callback=self.__foo, bouncetime=10)

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
        # self.__subscribeToButton(17, Button.UP)
        # self.__subscribeToButton(18, Button.DOWN)
        # self.__subscribeToButton(22, Button.MODE)
        # self.__subscribeToButton(27, Button.WAKE)

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
