from time import sleep

from frosti.core import ServiceConsumer, ThermostatState, ServiceProvider
from frosti.core.generics import GenericRelay


class MemoryOnlyRelay(GenericRelay):

    def __init__(self, function: ThermostatState):
        super().__init__(function)

    def openRelay(self):
        super().openRelay()

    def closeRelay(self):
        super().closeRelay()


class RelayManagementService(ServiceConsumer):
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

    def runDiagnostics(self):
        relays = [
            self.__relayMap[ThermostatState.FAN],
            self.__relayMap[ThermostatState.COOLING],
            self.__relayMap[ThermostatState.HEATING]
        ]

        for _ in range(10):
            for relay in relays:
                relay.closeRelay()
            sleep(0.25)
            for relay in relays:
                relay.openRelay()
            sleep(0.25)

        for a, b, c in [(0, 1, 2), (1, 2, 0), (2, 0, 1)]:
            for ra in [False, True]:
                relays[a].closeRelay() if ra else relays[a].openRelay()
                for rb in [False, True]:
                    relays[b].closeRelay() if rb else relays[b].openRelay()
                    for rc in [False, True]:
                        relays[c].closeRelay() if rc else relays[c].openRelay()
                        sleep(0.25)

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
