from queue import Queue
from curses import wrapper
import logging
import argparse

from src.logging import log, setupLogging
from src.events import EventBus
from src.api import ApiDataBroker, ApiMessageHandler
from src.settings import Settings, SettingsChangedEvent
from src.power import GoGriddyPriceChecker
from src.config import Config
from src.influx import InfluxDataExporter
from src.services import ServiceProvider


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

        self.__config = Config()
        self.installService(Config, self.__config)

        self.__settings = Settings()
        self.__settings.setServiceProvider(self)
        self.installService(Settings, self.__settings)

        # Put all the event handlers together
        self.__apiDataBroker = ApiDataBroker()
        self.__apiDataBroker.setServiceProvider(self)
        ApiMessageHandler.setup(self.__apiDataBroker)

    def __start(self, stdscr):
        if stdscr is not None:
            messageQueue = Queue(128)
            setupLogging(messageQueue)
            from src.terminal import TerminalThermostatDriver
            hardwareDriver = TerminalThermostatDriver(
                stdscr, messageQueue)
            hardwareDriver.setServiceProvider(self)
        else:
            from src.hardware import HardwareThermostatDriver
            hardwareDriver = HardwareThermostatDriver()
            hardwareDriver.setServiceProvider(self)
            setupLogging()

        # Setup the power price handler after the other event handlers have
        # been created so they get the first power events
        if self.__config.value('gogriddy', 'enabled'):
            try:
                priceChecker = GoGriddyPriceChecker()
                priceChecker.setServiceProvider(self)
            except ConnectionError:
                log.warning("Unable to reach GoGriddy")

        try:
            dataExporter = InfluxDataExporter()
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
