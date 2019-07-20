from flask import Flask
from queue import Queue
from threading import Thread
from time import sleep

from src.logging import log
from src.events import Event, EventBus, EventHandler
from src.thermostat import PropertyChangedEvent, \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


app = Flask(__name__)


class ApiEventHandler(EventHandler):
    """ Event handler thread dedicated to responding to the REST API for
    the thermostat.
    """
    __staticInstance = None

    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus)
        ApiEventHandler.__staticInstance = self

        self.__flaskThread = Thread(
            target=app.run,
            name='Flask Driver',
            args=("0.0.0.0", 5000))
        self.__flaskThread.daemon = True
        self.__flaskThread.start()

        self.__values = {
            TemperatureChangedEvent: 0,
            PressureChangedEvent: 0,
            HumidityChangedEvent: 0
        }

        super()._subscribe(TemperatureChangedEvent, self.__processFloat)
        super()._subscribe(PressureChangedEvent, self.__processFloat)
        super()._subscribe(HumidityChangedEvent, self.__processFloat)

    def __processFloat(self, event: PropertyChangedEvent):
        self.__values[type(event)] = event.value
        log.debug(f'ApiEventHandler Received {event} {event.value}')

    def getValue(self, eventType: type):
        return self.__values[eventType]

    @classmethod
    def getInstance(cls):
        return ApiEventHandler.__staticInstance

    @staticmethod
    @app.route('/api/version')
    def api_version():
        return "rpt-0.1"

    @staticmethod
    @app.route('/api/sensors/temperature')
    def api_sensor_temperature():
        apiEventHandler = ApiEventHandler.getInstance()
        return f"{apiEventHandler.getValue(TemperatureChangedEvent)}"

    @staticmethod
    @app.route('/api/sensors/pressure')
    def api_sensor_pressure():
        apiEventHandler = ApiEventHandler.getInstance()
        return f"{apiEventHandler.getValue(PressureChangedEvent)}"

    @staticmethod
    @app.route('/api/sensors/humidity')
    def api_sensor_humidity():
        apiEventHandler = ApiEventHandler.getInstance()
        return f"{apiEventHandler.getValue(HumidityChangedEvent)}"
