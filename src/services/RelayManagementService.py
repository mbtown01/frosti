from src.core import EventBusMember, ThermostatState, ServiceProvider
from src.core.generics import GenericRelay


class MemoryOnlyRelay(GenericRelay):

    def __init__(self, function: ThermostatState):
        super().__init__(function)

    def openRelay(self):
        super().openRelay()

    def closeRelay(self):
        super().closeRelay()


class RelayManagementService(EventBusMember):
    """ Service interface for relay management.  Subclassed by code tied into
    whatever actual relay exists """

    def __init__(self, relays: list=()):
        self.__relayMap = {r.function: r for r in relays}

        for state in ThermostatState:
            if state not in self.__relayMap:
                self.__relayMap[state] = MemoryOnlyRelay(state)

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        for relay in self.__relayMap.values():
            relay.openRelay()

    def openRelay(self, state: ThermostatState):
        """ Open the relay associated with the provided state """
        self.__relayMap[state].openRelay()

    def closeRelay(self, state: ThermostatState):
        """ Open the relay associated with the provided state """
        self.__relayMap[state].closeRelay()

    def getRelayStatus(self, state: ThermostatState):
        """ Returns boolean representing whether relay is open, or None if
        relay state is undefined """
        return self.__relayMap[state].isOpen
