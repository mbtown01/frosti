# pylint: disable=import-error
import RPi.GPIO as GPIO
# pylint: enable=import-error

from time import sleep

from src.core.generics import GenericRelay
from src.core import ThermostatState


class PanasonicAgqRelay(GenericRelay):

    def __init__(
            self, function: ThermostatState,
            pinIn: int, pinOut: int,
            delay: float=0.0):
        """ Relay edge-triggered by voltage across the in and out pins

        function: ThermostatState
            Thermostat state this relay controls
        pinIn: int
            Input-side pin
        pinout: int
            Output-side pin
        delay: float
            Fractional seconds to simply sleep after relay state is toggled
        """

        super().__init__(function)
        self.__pinIn = pinIn
        self.__pinOut = pinOut
        self.__delay = delay

        GPIO.setup(self.__pinIn, GPIO.OUT)
        GPIO.setup(self.__pinOut, GPIO.OUT)
        self.openRelay()

    def openRelay(self):
        # NEGATIVE 3V from IN->OUT opens the relay
        GPIO.output(self.__pinIn, False)
        GPIO.output(self.__pinOut, True)
        if self.isOpen is not None and not self.isOpen:
            sleep(self.__delay)

        super().openRelay()

    def closeRelay(self):
        # POSITIVE 3V from IN->OUT closes the relay
        GPIO.output(self.__pinIn, True)
        GPIO.output(self.__pinOut, False)
        if self.isOpen is not None and self.isOpen:
            sleep(self.__delay)

        super().closeRelay()
