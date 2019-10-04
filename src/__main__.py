from queue import Queue
from time import sleep
from curses import wrapper
from os import popen
import logging

from src.logging import log, setupLogging
from src.events import EventBus
from src.api import ApiEventHandler, ApiMessageHandler
from src.settings import settings, SettingsChangedEvent
from src.terminal import TerminalThermostatDriver
from src.power import GoGriddyEventHandler
from src.config import config
from src.influx import InfluxExportEventHandler


def main(stdscr):
    log.info('Starting thermostat main thread')

    # Build the initial event bus and connect the settings instance
    eventBus = EventBus()
    settings.setEventBus(eventBus)

    # Put all the event handlers together
    apiEventHandler = ApiEventHandler(eventBus)
    ApiMessageHandler.setup(apiEventHandler)
    apiEventHandler.start('API Event Driver')

    if stdscr is not None:
        messageQueue = Queue(128)
        setupLogging(messageQueue)
        hardwareDriver = TerminalThermostatDriver(
            stdscr, messageQueue, eventBus)
    else:
        from src.hardware import HardwareThermostatDriver
        hardwareDriver = HardwareThermostatDriver(eventBus)
        setupLogging()

    # Setup the power price handler after the other event handlers have
    # been created so they get the first power events
    if config.value('gogriddy', 'enabled'):
        try:
            powerPriceEventHandler = GoGriddyEventHandler(eventBus)
            powerPriceEventHandler.start("Power Price Event Handler")
        except ConnectionError:
            log.warning("Unable to reach GoGriddy")

    try:
        influxExportEventHandler = InfluxExportEventHandler(eventBus, 5)
        influxExportEventHandler.start('Influx Logger')
    except RuntimeError:
        log.warning("Influx logger failed to initialize")

    log.info('Entering into standard operation')
    eventBus.put(SettingsChangedEvent())
    hardwareDriver.exec()

if __name__ == '__main__':
    uname = popen('uname -a').read()
    if uname.find(' armv') >= 0:
        main(None)
    else:
        wrapper(main)
