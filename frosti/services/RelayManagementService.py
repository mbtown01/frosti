from frosti.core import ServiceConsumer, ThermostatState, ServiceProvider


class RelayManagementService(ServiceConsumer):
    """ Service interface for relay management.  Subclassed by code tied into
    whatever actual relay exists """

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        self.openRelay(ThermostatState.COOLING)
        self.openRelay(ThermostatState.HEATING)
        self.openRelay(ThermostatState.FAN)

    def openRelay(self, state: ThermostatState):
        raise NotImplementedError()

    def closeRelay(self, state: ThermostatState):
        raise NotImplementedError()

    def getRelayStatus(self, state: ThermostatState):
        raise NotImplementedError()
