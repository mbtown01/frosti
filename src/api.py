from flask import Flask, render_template, request, send_from_directory
from flask.logging import default_handler
from threading import Thread
import logging

from src.logging import log
from src.events import Event, EventBus, EventHandler
from src.thermostat import PropertyChangedEvent, \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


app = Flask(__name__, static_url_path='')


class ApiEventHandler(EventHandler):
    """ Event handler thread dedicated to responding to the REST API for
    the thermostat.
    """
    __instance = None

    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus)

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

    @staticmethod
    @app.route('/js/<path:path>')
    def serve_static(path):
        return send_from_directory('js', path)

    @staticmethod
    @app.route("/")
    def hello():
        return render_template(
            'index.html',
            temperature='72',# ApiEventHandler.sensor_temperature(),
            pressure=ApiEventHandler.sensor_pressure(),
            humidity=ApiEventHandler.sensor_humidity()
        )

    @staticmethod
    @app.route('/api/version')
    def version():
        return "rpt-0.1"

    @staticmethod
    @app.route('/api/mode', methods=['GET', 'POST'])
    def mode():
        if request.method == 'GET':
            return "MODE_STRING"
        if request.method == 'POST':
            log.debug(f"posted {request.form}")
        return None

    @staticmethod
    @app.route('/api/sensors/temperature')
    def sensor_temperature():
        apiEventHandler = ApiEventHandler.instance()
        return f"{apiEventHandler.getValue(TemperatureChangedEvent)}"

    @staticmethod
    @app.route('/api/sensors/pressure')
    def sensor_pressure():
        apiEventHandler = ApiEventHandler.instance()
        return f"{apiEventHandler.getValue(PressureChangedEvent)}"

    @staticmethod
    @app.route('/api/sensors/humidity')
    def sensor_humidity():
        apiEventHandler = ApiEventHandler.instance()
        return f"{apiEventHandler.getValue(HumidityChangedEvent)}"

    @staticmethod
    def createInstance(eventBus: EventBus):
        """ Send SettingsChangedEvent notifications to the provided event bus,
        or nowhere if eventBus is None
        """
        __class__.__instance = ApiEventHandler(eventBus)

    @staticmethod
    def instance():
        """ Returns the global instance
        """
        if __class__.__instance is None:
            raise RuntimeError("Instance of ApiEventHandler not instantiated")
        return __class__.__instance
