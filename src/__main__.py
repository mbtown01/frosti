from flask import Flask
from queue import Queue
from time import sleep

from src.hardware import SensorDriver
from src.settings import Settings
from src.events import FloatEvent, EventType, EventBus, EventHandler
from src.thermostat import ThermostatDriver
from src.api import ApiEventHandler


if __name__ == '__main__':
    eventBus = EventBus()

    sensorDriver = SensorDriver(eventBus)
    EventHandler.startEventHandler(sensorDriver, 'Sensor Driver')

    thermostat = ThermostatDriver(eventBus)
    EventHandler.startEventHandler(thermostat, 'Thermostat Driver')

    apiEventHandler = ApiEventHandler(eventBus)
    EventHandler.startEventHandler(apiEventHandler, 'API Event Driver')

    while(True):
        sleep(1.0)
