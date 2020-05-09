from queue import Queue
from curses import wrapper
import argparse
import RPi.GPIO as GPIO

from src.logging import log, setupLogging, handleException
from src.core import EventBus, ThermostatState
from src.core.generics import GenericEnvironmentSensor
from src.services import ConfigService, SettingsService, \
    SettingsChangedEvent, ApiDataBrokerService, GoGriddyPriceCheckService, \
    PostgresAdapterService, ThermostatService, EnvironmentSamplingService, \
    RelayManagementService
from src.core import ServiceProvider, ServiceConsumer


class RootDriver(ServiceProvider):

    def __init__(self):
        super().__init__()

        parser = argparse.ArgumentParser(
            description='RPT main process')
        parser.add_argument(
            '--hardware', choices=['term', 'v1', 'v2', 'auto'], default='term',
            help='Pick the underlying hardware supporting operations')
        parser.add_argument(
            '--diagnostics', default=False, action='store_true',
            help='Run hardware diagnostics and exit')
        self.__args = parser.parse_args()

    def __detectHardware(self):
        from board import SDA, SCL
        from busio import I2C
        i2c = I2C(SCL, SDA)
        results = i2c.scan()

        # Only Hardware v2 has the MCP23017 at address 0x20
        if 0x20 in results:
            return "v2"
        return "v1"

    def __installService(self, type, instance):
        if isinstance(instance, ServiceConsumer):
            instance.setServiceProvider(self)
        self.installService(type, instance)

    def __setupCore(self):
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
            self.__setupCore()

            self.sensor = GenericEnvironmentSensor()
            self.__installService(
                RelayManagementService, TerminalRelayManagementService())

            self.userInterface = \
                TerminalUserInterface(stdscr, self.sensor, messageQueue)
            self.userInterface.setServiceProvider(self)
        else:
            from src.hardware.PanasonicAgqRelay \
                import PanasonicAgqRelay as HardwareRelay
            from src.hardware.Bme280EnvironmentSensor \
                import Bme280EnvironmentSensor as HardwareEnvironmentSensor

            GPIO.setmode(GPIO.BCM)
            setupLogging()
            self.__setupCore()

            if self.__args.hardware == 'auto':
                self.__args.hardware = self.__detectHardware()
                log.info(f"Starting RPT on hardware {self.__args.hardware}")

            self.__args.hardware = 'v2'
            if self.__args.hardware == 'v1':
                from src.hardware.HardwareUserInterface_v1 \
                    import HardwareUserInterface_v1 as HardwareUserInterface
                relays = (
                    HardwareRelay(ThermostatState.FAN, 5, 17, delay=0.5),
                    HardwareRelay(ThermostatState.HEATING, 6, 27, delay=0.5),
                    HardwareRelay(ThermostatState.COOLING, 13, 22, delay=0.5)
                )
            elif self.__args.hardware == 'v2':
                from src.hardware.HardwareUserInterface_v2 \
                    import HardwareUserInterface_v2 as HardwareUserInterface
                relays = (
                    HardwareRelay(ThermostatState.FAN, 12, 6),
                    HardwareRelay(ThermostatState.HEATING, 21, 20),
                    HardwareRelay(ThermostatState.COOLING, 16, 19)
                )
            else:
                raise RuntimeError(
                    f'Hardware option {self.__args.hardware} not supported')

            self.sensor = HardwareEnvironmentSensor()
            relayManagementService = RelayManagementService(relays=relays)
            self.__installService(
                RelayManagementService, relayManagementService)
            if self.__args.diagnostics:
                relayManagementService.runDiagnostics()

            self.userInterface = HardwareUserInterface()
            self.userInterface.setServiceProvider(self)

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
            handleException("Postgres startup")

        self.__installService(
            EnvironmentSamplingService,
            EnvironmentSamplingService(self.sensor))

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
