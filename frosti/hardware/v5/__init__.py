from frosti.hardware.Bme280EnvironmentSamplingService \
    import Bme280EnvironmentSamplingService as EnvironmentSamplingService
from frosti.hardware.PanasonicAgqRelayManagementService \
    import PanasonicAgqRelayManagementService
from frosti.hardware.HardwareUserInterfaceService \
    import HardwareUserInterfaceService
from frosti.core import ThermostatState


class RelayManagementService(PanasonicAgqRelayManagementService):

    def __init__(self):
        super().__init__()

        self._configState(ThermostatState.FAN, 12, 26, 16)
        self._configState(ThermostatState.HEATING, 6, 13, 21)
        self._configState(ThermostatState.COOLING, 5, 19, 20)


class UserInterfaceService(HardwareUserInterfaceService):

    def __init__(self):
        super().__init__(
            scrnRstPin=14, scrnDcPin=17, scrnCsPin=4, scrnBusyPin=15,
            btnUpPin=23, btnDownPin=22, btnEnterPin=27
        )
