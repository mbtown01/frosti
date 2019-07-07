from flask import Flask
from queue import Queue
from threading import Thread

from hardware import SensorDriver
from settings import Settings
from interfaces import FloatEvent, EventType, EventBus
from thermostat import ThermostatDriver
from api import ApiEventHandler


if __name__ == '__main__':
    eventBus = EventBus()

    sensorDriver = SensorDriver(eventBus)
    sensorThread = Thread(
        target=sensorDriver.exec,
        name='Sensor Driver',
        args=())
    sensorThread.daemon = True
    sensorThread.start()

    settings = Settings()
    thermostat = ThermostatDriver(eventBus, settings)
    thermostatThread = Thread(
        target=thermostat.exec,
        name='Thermostat Driver',
        args=())
    thermostatThread.daemon = True
    thermostatThread.start()

    apiEventHandler = ApiEventHandler(eventBus)
    ApiEventHandler.setEventHandler(apiEventHandler)
    apiThread = Thread(
        target=apiEventHandler.exec,
        name='Api Event Handler',
        args=())
    apiThread.daemon = True
    apiThread.start()

    thermostatThread.join()
    sensorThread.join()
    apiThread.join()
