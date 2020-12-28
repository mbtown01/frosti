from frosti.core import ThermostatState
from frosti.services import RelayManagementService

import RPi.GPIO as GPIO


class RelayManagementService(RelayManagementService):
    """ Service interface for relay management.  Subclassed by code tied into
    whatever actual relay exists """

    def __init__(self):
        super().__init__()

        # (left, right, check) = (12, 26, 16)     # FAN
        # (left, right, check) = (6, 13, 21)      # HEAT
        # (left, right, check) = (5, 19, 20)      # COOL
        allPins = [12, 26, 6, 13, 5, 19]

        for pin in allPins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

        # GPIO.setup(check, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def openRelay(self, state: ThermostatState):
        """ Open the relay associated with the provided state """
        pass

    def closeRelay(self, state: ThermostatState):
        """ Open the relay associated with the provided state """
        pass

    def getRelayStatus(self, state: ThermostatState):
        """ Returns boolean representing whether relay is open, or None if
        relay state is undefined """
        pass
