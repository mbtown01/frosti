from frosti.core import ThermostatState
from frosti.services import RelayManagementService
from time import sleep
import RPi.GPIO as GPIO


class PanasonicAgqRelayManagementService(RelayManagementService):
    """ Service interface for relay management.  Subclassed by code tied into
    whatever actual relay exists """

    def __init__(self):
        super().__init__()

        self._pinConfig = dict()

    def _configState(self, state: ThermostatState,
                     pinLow: int, pinHi: int, pinCheck: int):

        self._pinConfig[state] = dict(
            pinLow=pinLow,
            pinHi=pinHi,
            pinCheck=pinCheck
        )

        GPIO.setup(pinLow, GPIO.OUT)
        GPIO.setup(pinHi, GPIO.OUT)
        GPIO.setup(pinCheck, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def _toggleRelay(self, pin1: int, pin2: int):
        GPIO.output(pin1, 0)
        GPIO.output(pin2, 1)
        sleep(0.1)
        GPIO.output(pin2, 0)

    def openRelay(self, state: ThermostatState):
        """ Open the relay associated with the provided state """
        self._toggleRelay(
            self._pinConfig[state]['pinLow'],
            self._pinConfig[state]['pinHi'],
        )

    def closeRelay(self, state: ThermostatState):
        """ Open the relay associated with the provided state """
        self._toggleRelay(
            self._pinConfig[state]['pinHi'],
            self._pinConfig[state]['pinLow'],
        )

    def isRelayOpen(self, state: ThermostatState):
        """ Returns boolean representing whether relay is open, or None if
        relay state is undefined """
        return GPIO.input(self._pinConfig[state]['pinCheck'])
