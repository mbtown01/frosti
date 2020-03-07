from queue import Queue
from curses import wrapper
import logging
import argparse

from src.logging import log, setupLogging
from src.core import EventBus
from src.services import ConfigService, SettingsService, \
    SettingsChangedEvent, ApiDataBrokerService, GoGriddyPriceCheckService, \
    InfluxDataExporterService
from src.core import ServiceProvider


class RootDriver(ServiceProvider):

    def __init__(self):
        super().__init__()

        parser = argparse.ArgumentParser(
            description='RPT main process')
        parser.add_argument(
            '--sim', dest='sim', action='store_true',
            help='Run the thermostat in simulation mode')
        self.__args = parser.parse_args()

        self.__eventBus = EventBus()
        self.installService(EventBus, self.__eventBus)

        self.__config = ConfigService()
        self.installService(ConfigService, self.__config)

        self.__settings = SettingsService()
        self.__settings.setServiceProvider(self)
        self.installService(SettingsService, self.__settings)

        # Put all the event handlers together
        self.__apiDataBroker = ApiDataBrokerService()
        self.__apiDataBroker.setServiceProvider(self)

    def __start(self, stdscr):
        if stdscr is not None:
            messageQueue = Queue(128)
            setupLogging(messageQueue)
            from src.terminal import TerminalThermostatService
            hardwareDriver = TerminalThermostatService(
                stdscr, messageQueue)
            hardwareDriver.setServiceProvider(self)
        else:
            from src.hardware import HardwareThermostatService
            hardwareDriver = HardwareThermostatService()
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
            dataExporter = InfluxDataExporterService()
            dataExporter.setServiceProvider(self)
        except Exception:
            log.warning("Influx logger failed to initialize")

        log.info('Entering into standard operation')
        self.__eventBus.fireEvent(SettingsChangedEvent())
        self.__eventBus.exec()

    def start(self):
        if self.__args.sim:
            wrapper(self.__start)
        else:
            self.__start(None)


if __name__ == '__main__':
    log.info('Starting thermostat main thread')

    rootDriver = RootDriver()
    rootDriver.start()
