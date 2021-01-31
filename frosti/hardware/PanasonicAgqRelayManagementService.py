from frosti.core import ThermostatState
from frosti.services import RelayManagementService


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

    def openRelay(self, state: ThermostatState):
        """ Open the relay associated with the provided state """
        pass

    def closeRelay(self, state: ThermostatState):
        """ Open the relay associated with the provided state """
        pass

    def isRelayOpen(self, state: ThermostatState):
        """ Returns boolean representing whether relay is open, or None if
        relay state is undefined """
        pass
