# pylint: disable=import-error
import RPi.GPIO as GPIO
# pylint: enable=import-error

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

    def openRelay(self):
        # NEGATIVE 3V from IN->OUT opens the relay
        GPIO.output(self.__pinIn, False)
        GPIO.output(self.__pinOut, True)
        super().openRelay()

    def closeRelay(self):
        # POSITIVE 3V from IN->OUT opens the relay
        GPIO.output(self.__pinIn, True)
        GPIO.output(self.__pinOut, False)
        super().closeRelay()
