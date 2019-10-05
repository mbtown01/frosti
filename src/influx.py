import json
import requests
import json
import sys

from influxdb import InfluxDBClient

from src.config import config
from src.logging import log
from src.settings import settings, Settings
from src.events import Event, EventBus, EventHandler
from src.generics import PropertyChangedEvent, \
    ThermostatStateChangedEvent, ThermostatState, \
    SensorDataChangedEvent


class InfluxExportEventHandler(EventHandler):

    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus)

        self.__unitName = config.resolve('thermostat', 'unitname')
        self.__lastState = ThermostatState.OFF
        self.__lastTemperature = 0
        self.__lastPressure = 0
        self.__lastHumidity = 0
        self.__hasData = False

        if not config.resolve("influxdb", "enabled", False):
            raise RuntimeError('InfluxDB is not configured')

        self.__client = InfluxDBClient(
            host=config.resolve("influxdb", "host"),
            port=config.resolve("influxdb", "port")
        )
        self.__client.switch_database(config.resolve("influxdb", "dbName"))
        self.__protocol = config.resolve("influxdb", "protocol")

        super()._installEventHandler(
            SensorDataChangedEvent, self.__processSensorDataChanged)
        super()._installEventHandler(
            ThermostatStateChangedEvent, self.__processThermostatStateChanged)

    def __processThermostatStateChanged(
            self, event: ThermostatStateChangedEvent):
        if self.__lastState != event.state:
            self.__lastState = event.state
            self.__updateInflux()

    def __processSensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.__lastPressure = event.pressure
        self.__lastHumidity = event.humidity
        self.__hasData = True

    def __updateInflux(self):
        cool = 0
        heat = 0
        if ThermostatState.COOLING == self.__lastState:
            cool = 1
        if ThermostatState.HEATING == self.__lastState:
            heat = 1

        entry = \
            f'rpt_status,unit={self.__unitName} ' + \
            f'temperature={self.__lastTemperature},' + \
            f'pressure={self.__lastPressure},' + \
            f'humidity={self.__lastHumidity},' + \
            f'cool={cool},heat={heat}'

        log.debug(entry)

        self.__client.write_points(entry, protocol=self.__protocol)
