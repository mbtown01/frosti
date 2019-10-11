import json
import requests
import json
import sys

from influxdb import InfluxDBClient
from threading import Thread

from src.config import Config
from src.services import ServiceProvider
from src.logging import log
from src.events import Event, EventBus, EventHandler
from src.generics import PropertyChangedEvent, \
    ThermostatStateChangedEvent, ThermostatState, \
    SensorDataChangedEvent, PowerPriceChangedEvent


class InfluxExportEventHandler(EventHandler):

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(Config)
        if not config.resolve("influxdb", "enabled", False):
            raise RuntimeError('InfluxDB is not configured')

        self.__unitName = config.resolve('thermostat', 'unitname')
        self.__influxHeader = f'rpt_status,unit={self.__unitName}'
        self.__lastSensorChangedEvent = None

        self.__client = InfluxDBClient(
            host=config.resolve("influxdb", "host"),
            port=config.resolve("influxdb", "port")
        )
        self.__client.switch_database(config.resolve("influxdb", "dbName"))
        self.__protocol = config.resolve("influxdb", "protocol")

        super()._installEventHandler(
            SensorDataChangedEvent, self.__sensorDataChanged)
        super()._installEventHandler(
            ThermostatStateChangedEvent, self.__thermostatStateChanged)
        super()._installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        self.__updateInflux(f'price={event.price}')

    def __thermostatStateChanged(self, event: ThermostatStateChangedEvent):
        cool = 1 if ThermostatState.COOLING == event.state else 0
        heat = 1 if ThermostatState.HEATING == event.state else 0
        fan = 1 if ThermostatState.FAN == event.state else 0
        self.__updateInflux(f'cool={cool},heat={heat},fan={fan}')

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        self.__updateInflux(
            f'temperature={event.temperature},'
            f'pressure={event.pressure},'
            f'humidity={event.humidity}'
        )

    def __updateInflux(self, data: str):
        entry = f'{self.__influxHeader} {data}'
        try:
            self.__client.write_points(entry, protocol=self.__protocol)
            log.debug(entry)
        except:
            log.warning("Failed connecting to influx")
