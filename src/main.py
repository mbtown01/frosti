from flask import Flask
from queue import Queue

from hardware import SensorDriver
from time import sleep
from settings import Settings
from interfaces import FloatEvent, EventType, EventBus, EventHandler
from thermostat import ThermostatDriver
from api import ApiEventHandler


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
