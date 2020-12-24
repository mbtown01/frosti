from frosti.core import ThermostatState
from frosti.services import RelayManagementService


class RelayManagementService(RelayManagementService):
    """ Service interface for relay management.  Subclassed by code tied into
    whatever actual relay exists """

    def __init__(self):
        super().__init__()

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
