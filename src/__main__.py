from queue import Queue
from time import sleep
from curses import wrapper
from os import popen
import logging

from src.logging import log, setupLogging
from src.events import EventBus
from src.thermostat import ThermostatDriver
from src.api import ApiEventHandler, ApiMessageHandler
from src.settings import settings, SettingsChangedEvent
from src.terminal import TerminalHardwareDriver
from src.power import GoGriddyEventHandler
from src.config import config


def main(stdscr):
    log.info('Starting thermostat main thread')

    # Build the initial event bus and connect the settings instance
    eventBus = EventBus()
    settings.setEventBus(eventBus)

    # Put all the event handlers together
    apiEventHandler = ApiEventHandler(eventBus)
    thermostat = ThermostatDriver(eventBus)

    # Put the initial settings out to all participants so it's the
    # first event they process
    apiEventHandler.start('API Event Driver')
    thermostat.start('Thermostat Driver')
    ApiMessageHandler.setup(apiEventHandler)

    if stdscr is not None:
        messageQueue = Queue(128)
        setupLogging(messageQueue)
        hardwareDriver = TerminalHardwareDriver(
            stdscr, messageQueue, eventBus)
    else:
        from src.hardware import HardwareDriver
        hardwareDriver = HardwareDriver(eventBus)
        setupLogging()

    # Setup the power price handler after the other event handlers have
    # been created so they get the first power events
    if config.gogriddy_enabled:
        try:
            powerPriceEventHandler = GoGriddyEventHandler(eventBus)
            powerPriceEventHandler.start("Power Price Event Handler")
        except ConnectionError:
            log.warning("Unable to reach GoGriddy")

    # Start all handlers on their own theads
    hardwareDriver.start('Hardware Driver')

    log.info('Entering into standard operation')
    eventBus.put(SettingsChangedEvent())
    hardwareDriver.join()

if __name__ == '__main__':
    uname = popen('uname -a').read()
    if uname.find(' armv') >= 0:
        main(None)
    else:
        wrapper(main)
