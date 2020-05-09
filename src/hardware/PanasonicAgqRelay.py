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

    def __toggleRelay(self, a: int, b: int):
        GPIO.output(a, False)
        GPIO.output(b, True)
        # sleep(0.1)
        # GPIO.output(b, False)

    def openRelay(self):
        # NEGATIVE 3V from IN->OUT opens the relay
        self.__toggleRelay(self.__pinIn, self.__pinOut)
        super().openRelay()

    def closeRelay(self):
        # POSITIVE 3V from IN->OUT opens the relay
        self.__toggleRelay(self.__pinOut, self.__pinIn)
        super().closeRelay()
