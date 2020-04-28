from queue import Queue
from curses import wrapper
from sys import exc_info
import argparse

from src.logging import log, setupLogging
from src.core import EventBus, ThermostatState
from src.core.generics import GenericEnvironmentSensor
from src.services import ConfigService, SettingsService, \
    SettingsChangedEvent, ApiDataBrokerService, GoGriddyPriceCheckService, \
    PostgresAdapterService, ThermostatService, EnvironmentSamplingService, \
    RelayManagementService
from src.core import ServiceProvider


class RootDriver(ServiceProvider):

    def __init__(self):
        super().__init__()

        parser = argparse.ArgumentParser(
            description='RPT main process')
        parser.add_argument(
            '--hardware', choices=['term', 'v1', 'v2'], default='term',
            help='Pick the underlying hardware supporting operations')
        self.__args = parser.parse_args()

        self.__eventBus = EventBus()
        self.installService(EventBus, self.__eventBus)

        self.__config = ConfigService()
        self.installService(ConfigService, self.__config)

        self.__settings = SettingsService()
        self.__settings.setServiceProvider(self)
        self.installService(SettingsService, self.__settings)

        self.__thermostat = ThermostatService()
        self.__thermostat.setServiceProvider(self)
        self.installService(ThermostatService, self.__thermostat)

        # Put all the event handlers together
        self.__apiDataBroker = ApiDataBrokerService()
        self.__apiDataBroker.setServiceProvider(self)

    def __start(self, stdscr):
        if stdscr is not None:
            from src.terminal import TerminalRelayManagementService, \
                TerminalUserInterface

            messageQueue = Queue(128)
            setupLogging(messageQueue)

            self.sensor = GenericEnvironmentSensor()
            self.environmentSampling = \
                EnvironmentSamplingService(self.sensor)
            self.environmentSampling.setServiceProvider(self)
            self.installService(
                EnvironmentSamplingService, self.environmentSampling)

            self.relayManagement = TerminalRelayManagementService()
            self.relayManagement.setServiceProvider(self)
            self.installService(RelayManagementService, self.relayManagement)

            self.userInterface = \
                TerminalUserInterface(stdscr, self.sensor, messageQueue)
            self.userInterface.setServiceProvider(self)
        else:
            from src.hardware.PanasonicAgqRelay import PanasonicAgqRelay
            if self.__args.hardware == 'v1':
                from src.hardware.HardwareUserInterface_v1 \
                    import HardwareUserInterface_v1 as HardwareUserInterface
                from src.hardware.Bme280EnvironmentSensor \
                    import Bme280EnvironmentSensor as HardwareEnvironmentSensor
                relays = (
                    PanasonicAgqRelay(ThermostatState.FAN, 5, 17),
                    PanasonicAgqRelay(ThermostatState.HEATING, 6, 27),
                    PanasonicAgqRelay(ThermostatState.COOLING, 13, 22)
                )
            elif self.__args.hardware == 'v2':
                from src.hardware.HardwareUserInterface_v2 \
                    import HardwareUserInterface_v2 as HardwareUserInterface
                from src.hardware.Bme280EnvironmentSensor \
                    import Bme280EnvironmentSensor as HardwareEnvironmentSensor
                relays = (
                    PanasonicAgqRelay(ThermostatState.FAN, 12, 6),
                    PanasonicAgqRelay(ThermostatState.HEATING, 21, 20),
                    PanasonicAgqRelay(ThermostatState.COOLING, 16, 19)
                )
            else:
                raise RuntimeError(
                    f'Hardware oprtion {self.__args.hardware} not supported')

            self.sensor = HardwareEnvironmentSensor()
            self.environmentSampling = \
                EnvironmentSamplingService(self.sensor)
            self.environmentSampling.setServiceProvider(self)
            self.installService(
                EnvironmentSamplingService, self.environmentSampling)

            self.relayManagement = RelayManagementService(relays=relays)
            self.relayManagement.setServiceProvider(self)
            self.installService(RelayManagementService, self.relayManagement)

            hardwareDriver = HardwareUserInterface()
            hardwareDriver.setServiceProvider(self)
            setupLogging()

        # Setup the power price handler after the other event handlers have
        # been created so they get the first power events
        if self.__config.value('gogriddy', 'enabled'):
            try:
                priceChecker = GoGriddyPriceCheckService()
                priceChecker.setServiceProvider(self)
            except ConnectionError:
                log.warning("Unable to reach GoGriddy")

        try:
            dataExporter = PostgresAdapterService()
            dataExporter.setServiceProvider(self)
        except:
            info = exc_info()
            log.warning(f"Postgres startup encountered exception: {info}")

        log.info('Entering into standard operation')
        self.__eventBus.fireEvent(SettingsChangedEvent())
        self.__eventBus.exec()

    def start(self):
        if self.__args.hardware == 'term':
            wrapper(self.__start)
        else:
            self.__start(None)


if __name__ == '__main__':
    log.info('Starting thermostat main thread')

    rootDriver = RootDriver()
    rootDriver.start()
