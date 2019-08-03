from queue import Queue
from time import sleep
from curses import wrapper
import logging

from src.events import EventBus
from src.thermostat import ThermostatDriver
from src.api import ApiEventHandler
from src.settings import Settings, SettingsChangedEvent
from src.logging import log, setupLogging
from src.terminal import TerminalHardwareDriver


def main(stdscr):
    # Build the initial event bus and connect the settings instance
    eventBus = EventBus()
    Settings.instance().setEventBus(eventBus)

    # Put all the event handlers together
    ApiEventHandler.createInstance(eventBus)
    thermostat = ThermostatDriver(eventBus)

    # Put the initial settings out to all participants so it's the
    # first event they process
    ApiEventHandler.instance().start('API Event Driver')
    thermostat.start('Thermostat Driver')

    try:
        from src.hardware import HardwareDriver
        hardwareDriver = HardwareDriver(eventBus)
        setupLogging()
    except ModuleNotFoundError:
        messageQueue = Queue(128)
        setupLogging(messageQueue)
        hardwareDriver = TerminalHardwareDriver(
            stdscr, messageQueue, eventBus)

    # Start all handlers on their own theads
    hardwareDriver.start('Hardware Driver')

    log.info('Entering into standard operation')
    eventBus.put(SettingsChangedEvent())
    hardwareDriver.join()

if __name__ == '__main__':
    wrapper(main)
