from flask import Flask
from queue import Queue
from time import sleep
import logging

from src.events import EventBus, EventHandler
from src.thermostat import ThermostatDriver
from src.api import ApiEventHandler
from src.settings import SettingsChangedEvent, Settings
from src.logging import log, setupLogging
from src.terminal import TerminalHardwareDriver


def main():
    setupLogging()
    log.info('Initializing thermostat')

    # Start all the event handlers
    eventBus = EventBus()
    thermostat = ThermostatDriver(eventBus)
    apiEventHandler = ApiEventHandler(eventBus)
    try:
        from src.hardware import HardwareDriver
        hardwareDriver = HardwareDriver(eventBus)
    except ModuleNotFoundError:
        hardwareDriver = TerminalHardwareDriver(eventBus)

    # Put the initial settings out to all participants so it's the
    # first event they process
    eventBus.put(SettingsChangedEvent(Settings()))

    # Start all handlers on their own theads
    hardwareDriver.start('Hardware Driver')
    thermostat.start('Thermostat Driver')
    apiEventHandler.start('API Event Driver')

    log.info('Entering into standard operation')
    hardwareDriver.join()

if __name__ == '__main__':
    main()
