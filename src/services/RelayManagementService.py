from src.core import EventBusMember, ThermostatState, ServiceProvider
from src.core.generics import GenericRelay


class RelayManagementService(EventBusMember):
    """ Service interface for relay management.  Subclassed by code tied into
    whatever actual relay exists """

    def __init__(self, relays: dict):
        self.__relayMap = {r.function: r for r in relays}
        if ThermostatState.OFF not in self.__relayMap:
            self.__relayMap[ThermostatState.OFF] = \
                GenericRelay(ThermostatState.OFF)

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
