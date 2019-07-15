# pylint: disable=import-error
import board
import busio
import adafruit_bme280
import adafruit_character_lcd.character_lcd_i2c as characterlcd
import RPi.GPIO as GPIO

# pylint: enable=import-error

from queue import Queue

from src.logging import log
from src.events import EventBus, EventHandler
from src.thermostat import \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


class HardwareDriver(EventHandler):

    class Button:
        def __init__(self, name: str, pin: int):
            self.__name = name
            self.__pin = pin
            self.__isPressed = False

            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        def query(self):
            isPressed = bool(GPIO.input(self.__pin))
            rtn = isPressed and not self.__isPressed
            self.__isPressed = isPressed
            if rtn:
                log.debug(f"Button '{self.__name}' pressed'")

            return rtn

    def __init__(self, eventBus: EventBus):
        GPIO.setmode(GPIO.BCM)

        loopSleep = 0.05
        self.__sampleInterval = int(5/loopSleep)
        self.__counter = 0
        self.__i2c = busio.I2C(board.SCL, board.SDA)
        self.__i2c2 = busio.I2C(board.SCL, board.SDA)
        self.__bme280 = \
            adafruit_bme280.Adafruit_BME280_I2C(self.__i2c, address=0x76)
        self.__lcd = characterlcd.Character_LCD_I2C(self.__i2c2, 16, 2)

        self.__lcd.clear()
        self.__lcd.backlight = True
        self.__lcd.message = "this is a test\nas you can see"

        self.__buttons = {
            'mode': HardwareDriver.Button('Mode', 16),
            'up': HardwareDriver.Button('Up', 20),
            'down': HardwareDriver.Button('Down', 21),
        }

        super().__init__(eventBus, loopSleep)

    def processEvents(self):
        super().processEvents()

        for name, button in self.__buttons.items():
            button.query()

        # Only update measurements at the sample interval
        self.__counter += 1
        if 0 == self.__counter % self.__sampleInterval:
            super()._fireEvent(TemperatureChangedEvent(
                self.__bme280.temperature*9.0/5.0+32.0))
            super()._fireEvent(PressureChangedEvent(
                self.__bme280.pressure))
            super()._fireEvent(HumidityChangedEvent(
                self.__bme280.humidity))

        # Additional scanning should be done for user buttons here
