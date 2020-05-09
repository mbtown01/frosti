from time import sleep

# pylint: disable=import-error
import RPi.GPIO as GPIO
import board
from busio import I2C
from digitalio import Direction, Pull
from adafruit_mcp230xx.mcp23017 import MCP23017
# pylint: enable=import-error

from .HD44780Display import HD44780Display
from .LtrbRasfRgbLed import LtrbRasfRgbLed
from src.core import EventBus, ServiceProvider
from src.core.generics import GenericUserInterface, GenericRgbLed


class HardwareUserInterface_v2(GenericUserInterface):

    def __init__(self):
        GPIO.setup(17, GPIO.IN, GPIO.PUD_UP)

        self.__i2c = I2C(board.SCL, board.SDA)
        self.__mcp = MCP23017(self.__i2c)
        self.__buttonMap = {
            6: GenericUserInterface.Button.WAKE,
            5: GenericUserInterface.Button.MODE,
            10: GenericUserInterface.Button.UP,
            11: GenericUserInterface.Button.DOWN,
        }

        pinsEnabled = 0
        for p in self.__buttonMap.keys():
            pin = self.__mcp.get_pin(p)
            pin.direction = Direction.INPUT
            pin.pull = Pull.UP
            pinsEnabled = pinsEnabled | 1 << p

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

        self.__lcd = HD44780Display(0x27, 20, 4)
        self.__rgbLeds = (
            LtrbRasfRgbLed(self.__mcp, 13, 14, 12),
            LtrbRasfRgbLed(self.__mcp, 3, 4, 2),
        )

        # 12, 13, 14 is LEFT B, R, G
        # 2, 3, 4 is RIGHT B, R, G
        super().__init__(lcd=self.__lcd, rgbLeds=self.__rgbLeds)

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        GPIO.add_event_detect(
            17, GPIO.FALLING, callback=self.__mcp23017_callback)

        for color in GenericRgbLed.Color:
            for led in self.__rgbLeds:
                led.setColor(color)
            sleep(0.25)
        for led in self.__rgbLeds:
            led.setColor(GenericRgbLed.Color.BLACK)

    def __mcp23017_callback(self, port):
        int_flag = self.__mcp.int_flag
        self.__mcp.clear_ints()

        for p in int_flag:
            button = self.__buttonMap.get(p)
            if button is not None:
                pin = self.__mcp.get_pin(p)
                if not pin.value:
                    eventBus = self._getService(EventBus)
                    eventBus.fireEvent(
                        GenericUserInterface.ButtonPressedEvent(button))
