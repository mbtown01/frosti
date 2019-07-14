from flask import Flask
from queue import Queue
from time import sleep
import logging

from src.hardware import SensorDriver
from src.events import EventBus, EventHandler
from src.thermostat import ThermostatDriver
from src.api import ApiEventHandler
from src.settings import SettingsChangedEvent, Settings
from src.logging import log, setupLogging


if __name__ == '__main__':
    setupLogging()
    log.info('Initializing thermostat')

    eventBus = EventBus()

    # Start all the event handlers
    sensorDriver = SensorDriver(eventBus)
    EventHandler.startEventHandler(sensorDriver, 'Sensor Driver')

    thermostat = ThermostatDriver(eventBus)
    EventHandler.startEventHandler(thermostat, 'Thermostat Driver')

    apiEventHandler = ApiEventHandler(eventBus)
    EventHandler.startEventHandler(apiEventHandler, 'API Event Driver')

    # Put the initial settings out to all participants
    eventBus.put(SettingsChangedEvent(Settings()))

    log.info('Entering into standard operation')
    while(True):
        sleep(1.0)
