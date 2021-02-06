# This file is necessary for the tests written in this folder to
# successfully import logic from frosti

# from .HardwareUserInterface_v1 import HardwareUserInterface_v1
# from .HardwareUserInterface_v2 import HardwareUserInterface_v2

from frosti.core import ThermostatState, ServiceProvider
from frosti.services import \
    RelayManagementService, UserInterfaceService, EnvironmentSamplingService

from .Bme280EnvironmentSamplingService \
    import Bme280EnvironmentSamplingService
from .PanasonicAgqRelayManagementService \
    import PanasonicAgqRelayManagementService
from .HardwareUserInterfaceService \
    import HardwareUserInterfaceService


# class RelayManagementService(PanasonicAgqRelayManagementService):

#     def __init__(self):
#         super().__init__()

#         self._configState(ThermostatState.FAN, 12, 26, 16)
#         self._configState(ThermostatState.HEATING, 6, 13, 21)
#         self._configState(ThermostatState.COOLING, 5, 19, 20)


# class UserInterfaceService(HardwareUserInterfaceService):

#     def __init__(self):
#         super().__init__(
#             scrnRstPin=14, scrnDcPin=17, scrnCsPin=4, scrnBusyPin=15,
#             btnUpPin=23, btnDownPin=22, btnEnterPin=27
#         )


def hardware_init(serviceProvider: ServiceProvider, hardwareName: str):

    if hardwareName == 'v5':
        service = PanasonicAgqRelayManagementService()
        service._configState(ThermostatState.FAN, 12, 26, 16)
        service._configState(ThermostatState.HEATING, 6, 13, 21)
        service._configState(ThermostatState.COOLING, 5, 19, 20)

        service.setServiceProvider(serviceProvider)
        serviceProvider.installService(RelayManagementService, service)

        # service = Bme280EnvironmentSamplingService()
        # service.setServiceProvider(self)
        # self.installService(EnvironmentSamplingService, service)

        # service = HardwareUserInterfaceService(
        #     scrnRstPin=14, scrnDcPin=17, scrnCsPin=4, scrnBusyPin=15,
        #     btnUpPin=23, btnDownPin=22, btnEnterPin=27)
        # service.setServiceProvider(self)
        # self.installService(UserInterfaceService, service)
    elif hardwareName == 'v6':
        service = PanasonicAgqRelayManagementService()
        service._configState(ThermostatState.FAN, 25, 14, 22)
        service._configState(ThermostatState.HEATING, 23, 18, 17)
        service._configState(ThermostatState.COOLING, 24, 15, 27)
        service.setServiceProvider(serviceProvider)
        serviceProvider.installService(RelayManagementService, service)

        # from time import sleep
        # print("Relays should all be closed, start testing!!")
        # stateList = [ThermostatState.COOLING,
        #              ThermostatState.HEATING, ThermostatState.FAN]
        # sleep(2)
        # for state in [ThermostatState.HEATING]:
        #     for i in range(5000):
        #         for state in stateList:
        #             print(f"OPEN {state}")
        #             service.openRelay(state)
        #             print(f"STATE {service.isRelayOpen(state)}")
        #         sleep(2)
        #         for state in stateList:
        #             print(f"CLOSE {state}")
        #             service.closeRelay(state)
        #             print(f"STATE {service.isRelayOpen(state)}")
        #         sleep(2)

        service = Bme280EnvironmentSamplingService()
        service.setServiceProvider(serviceProvider)
        serviceProvider.installService(EnvironmentSamplingService, service)

        service = HardwareUserInterfaceService(
            scrnRstPin=20, scrnDcPin=21, scrnCsPin=12, scrnBusyPin=16,
            btnUpPin=13, btnDownPin=1, btnEnterPin=26
            # btnUpPin=13, btnDownPin=19, btnEnterPin=26
            # btnUpPin=8, btnDownPin=1, btnEnterPin=7
        )
        service.setServiceProvider(serviceProvider)
        serviceProvider.installService(UserInterfaceService, service)
    else:
        raise RuntimeError(
            f'Hardware option {hardwareName} not supported')
