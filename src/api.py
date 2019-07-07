from flask import Flask
from queue import Queue
from threading import Thread
from time import sleep

from hardware import SensorDriver
from settings import Settings
from interfaces import FloatEvent, EventType, EventBus, EventHandler
from thermostat import ThermostatDriver


app = Flask(__name__)


class ApiEventHandler(EventHandler):
    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus)

        self.__values = {
            EventType.TEMPERATURE: 0,
            EventType.PRESSURE: 0,
            EventType.HUMIDITY: 0
        }

        super()._subscribe(EventType.TEMPERATURE, self.processFloat)
        super()._subscribe(EventType.PRESSURE, self.processFloat)
        super()._subscribe(EventType.HUMIDITY, self.processFloat)

    def processFloat(self, event: FloatEvent):
        self.__values[event.getType()] = event.getValue()
        print(f'ApiEvevtHandler Received {event.getType()} {event.getValue()}')

    def getValue(self, eventType: EventType):
        return self.__values[eventType]

    @staticmethod
    @app.route('/api/version')
    def api_version():
        return "rpt-0.1"

    @staticmethod
    @app.route('/api/sensors/temperature')
    def api_sensor_temperature():
        apiEventHandler = ApiEventHandler.getInstance()
        return f"{apiEventHandler.getValue(EventType.TEMPERATURE)}"

    @staticmethod
    @app.route('/api/sensors/pressure')
    def api_sensor_pressure():
        apiEventHandler = ApiEventHandler.getInstance()
        return f"{apiEventHandler.getValue(EventType.PRESSURE)}"

    @staticmethod
    @app.route('/api/sensors/humidity')
    def api_sensor_humidity():
        apiEventHandler = ApiEventHandler.getInstance()
        return f"{apiEventHandler.getValue(EventType.HUMIDITY)}"

    def exec(self):
        flaskThread = Thread(
            target=app.run,
            name='Flask Driver',
            args=("0.0.0.0", 5000))
        flaskThread.daemon = True
        flaskThread.start()

        while True:
            sleep(1)
            super()._processEvents()
