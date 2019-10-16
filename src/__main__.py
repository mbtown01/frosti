from queue import Queue
from curses import wrapper
from os import popen
from time import sleep
import logging

from src.logging import log, setupLogging
from src.events import EventBus
from src.api import ApiDataBroker, ApiMessageHandler
from src.settings import Settings, SettingsChangedEvent
from src.terminal import TerminalThermostatDriver
from src.power import GoGriddyPriceChecker
from src.config import Config
from src.influx import InfluxDataExporter
from src.services import ServiceProvider


def main(stdscr):
    log.info('Starting thermostat main thread')

    serviceProvider = ServiceProvider()

    # Build the initial event bus and connect the settings instance
    eventBus = EventBus()
    serviceProvider.installService(EventBus, eventBus)

    config = Config()
    serviceProvider.installService(Config, config)

    settings = Settings()
    settings.setServiceProvider(serviceProvider)
    serviceProvider.installService(Settings, settings)

    # Put all the event handlers together
    apiDataBroker = ApiDataBroker()
    apiDataBroker.setServiceProvider(serviceProvider)
    ApiMessageHandler.setup(apiDataBroker)

    if stdscr is not None:
        messageQueue = Queue(128)
        setupLogging(messageQueue)
        hardwareDriver = TerminalThermostatDriver(
            stdscr, messageQueue)
        hardwareDriver.setServiceProvider(serviceProvider)
    else:
        from src.hardware import HardwareThermostatDriver
        hardwareDriver = HardwareThermostatDriver()
        hardwareDriver.setServiceProvider(serviceProvider)
        setupLogging()

    # Setup the power price handler after the other event handlers have
    # been created so they get the first power events
    if config.value('gogriddy', 'enabled'):
        try:
            priceChecker = GoGriddyPriceChecker()
            priceChecker.setServiceProvider(serviceProvider)
        except ConnectionError:
            log.warning("Unable to reach GoGriddy")

    try:
        dataExporter = InfluxDataExporter()
        dataExporter.setServiceProvider(serviceProvider)
    except RuntimeError:
        log.warning("Influx logger failed to initialize")

    log.info('Entering into standard operation')
    eventBus.fireEvent(SettingsChangedEvent())
    eventBus.exec()


if __name__ == '__main__':
    uname = popen('uname -a').read()
    if uname.find(' armv') >= 0:
        main(None)
    else:
        wrapper(main)
