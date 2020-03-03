# pylint: disable=import-error
import board
import smbus
import busio
import adafruit_bme280
import RPi.GPIO as GPIO
# pylint: enable=import-error

from time import sleep

from src.core.generics import GenericRelay
from src.core import ThermostatState


class PanasonicAgqRelay(GenericRelay):

    def __init__(self, function: ThermostatState, pinIn: int, pinOut: int):
        super().__init__(function)
        self.__pinIn = pinIn
        self.__pinOut = pinOut

        GPIO.setup(self.__pinIn, GPIO.OUT)
        GPIO.setup(self.__pinOut, GPIO.OUT)
        self.openRelay()

    def _openRelay(self):
        # NEGATIVE 3V from IN->OUT opens the relay
        GPIO.output(self.__pinIn, False)
        GPIO.output(self.__pinOut, True)
        sleep(0.1)
        GPIO.output(self.__pinOut, False)

    def _closeRelay(self):
        # POSITIVE 3V from IN->OUT opens the relay
        GPIO.output(self.__pinIn, True)
        sleep(0.1)
        GPIO.output(self.__pinIn, False)
