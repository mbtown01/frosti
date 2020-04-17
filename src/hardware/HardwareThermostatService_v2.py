# pylint: disable=import-error
import RPi.GPIO as GPIO
import board

from busio import I2C
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

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        # Link a GPIO pin from the 23017 to a button action
        self.__buttonMap = {
            6: Button.WAKE,
            5: Button.MODE,
            10: Button.UP,
            11: Button.DOWN,
        }

        sensor = Bme280EnvironmentSensor()

        super().__init__(
            lcd=HD44780Display(0x27, 20, 4),
            sensor=sensor,
            relays=(
                PanasonicAgqRelay(ThermostatState.FAN, 12, 6),
                PanasonicAgqRelay(ThermostatState.HEATING, 21, 20),
                PanasonicAgqRelay(ThermostatState.COOLING, 16, 19)
            )
        )

    def __mcp23017_callback(self, port):
        int_flag = self.__mcp.int_flag
        self.__mcp.clear_ints()

        log.debug(f"INTERRUPT on 17, {int_flag}")

        for p in int_flag:
            button = self.__buttonMap.get(p)
            if button is not None:
                pin = self.__mcp.get_pin(p)
                if not pin.value:
                    log.debug(f"   {button}, {p}")
                    self._fireEvent(ButtonPressedEvent(button))

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        self._installEventHandler(
            ButtonPressedEvent, self.__buttonPressedHandler)

        GPIO.setup(17, GPIO.IN, GPIO.PUD_UP)
        GPIO.add_event_detect(
            17, GPIO.FALLING, callback=self.__mcp23017_callback)

        self.__i2c = I2C(board.SCL, board.SDA)
        self.__mcp = MCP23017(self.__i2c)

        pinsEnabled = 0
        for p in self.__buttonMap.keys():
            pin = self.__mcp.get_pin(p)
            pin.direction = Direction.INPUT
            pin.pull = Pull.UP
            pinsEnabled = pinsEnabled | 1 << p

        for p in [2, 3, 4, 12, 13, 14]:
            pin = self.__mcp.get_pin(p)
            pin.direction = Direction.OUTPUT
            pin.value = 1

        # Only docs for this I could find are at
        # https://github.com/adafruit/Adafruit_CircuitPython_MCP230xx/blob/master/examples/mcp230xx_event_detect_interrupt.py

        # GPINTEN controls interrupt-on-change feature per pin
        self.__mcp.interrupt_enable = pinsEnabled
        # INTCON Interrupt control register
        self.__mcp.interrupt_configuration = 0x0000
        # DEFVAL controls default comparison value
        self.__mcp.default_value = 0xFFFF
        # Interrupt as open drain and mirrored
        self.__mcp.io_control = 0x44

        self.__mcp.clear_ints()  # Interrupts need to be cleared initially

    def __buttonPressedHandler(self, event: ButtonPressedEvent):
        if event.button == Button.UP:
            super()._modifyComfortSettings(1)
        elif event.button == Button.DOWN:
            super()._modifyComfortSettings(-1)
        elif event.button == Button.MODE:
            super()._nextMode()
