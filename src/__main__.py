from queue import Queue
from curses import wrapper
from sys import exc_info
import logging
import argparse

from src.logging import log, setupLogging
from src.core import EventBus
from src.services import ConfigService, SettingsService, \
    SettingsChangedEvent, ApiDataBrokerService, GoGriddyPriceCheckService, \
    PostgresAdapterService
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
        elif self.__args.hardware == 'v1':
            from src.hardware.HardwareThermostatService_v1 \
                import HardwareThermostatService_v1
            hardwareDriver = HardwareThermostatService_v1()
            hardwareDriver.setServiceProvider(self)
            setupLogging()
        elif self.__args.hardware == 'v2':
            from src.hardware.HardwareThermostatService_v2 \
                import HardwareThermostatService_v2
            hardwareDriver = HardwareThermostatService_v2()
            hardwareDriver.setServiceProvider(self)
            setupLogging()
        else:
            raise RuntimeError(
                f'Hardware oprtion {self.__args.hardware} not supported')

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
