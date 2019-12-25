import json
import requests
import json
import sys

from influxdb import InfluxDBClient
from threading import Thread

from src.config import Config
from src.services import ServiceProvider
from src.logging import log
from src.settings import Settings, SettingsChangedEvent
from src.events import Event, EventBus, EventBusMember
from src.generics import PropertyChangedEvent, \
    ThermostatStateChangedEvent, ThermostatState, \
    SensorDataChangedEvent, PowerPriceChangedEvent


class InfluxDataExporter(EventBusMember):

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(Config)
        if not config.resolve("influxdb", "enabled", False):
            raise RuntimeError('InfluxDB is not configured')

        self.__unitName = config.resolve('thermostat', 'unitname')
        self.__influxHeader = f'rpt_status,unit={self.__unitName}'
        self.__lastSensorChangedEvent = None
        self.__protocol = config.resolve("influxdb", "protocol")

        self.__client = InfluxDBClient(
            host=config.resolve("influxdb", "host"),
            port=config.resolve("influxdb", "port"),
            username='rpt',
            password='rpt'
        )

        try:
            dbName = config.resolve("influxdb", "dbName")
            hashList = self.__client.get_list_database()
            nameList = list(map(lambda x: x['name'], hashList))
            if dbName not in nameList:
                self.__client.create_database(dbName)
            self.__client.switch_database(dbName)

            # Grab the last settings for this thermostat
            query = \
                "select last(comfortMin) as min, " \
                "       last(comfortMax) as max " \
                "from rpt_status " \
                f"where unit='{self.__unitName}'"
            resultSet = self.__client.query(query)
            if resultSet.error is not None:
                raise RuntimeError(str(resultSet.error))
            values = list(resultSet.get_points())
            if len(values):
                settings = self._getService(Settings)
                settings.comfortMin = values[0]['min']
                settings.comfortMax = values[0]['max']

            super()._installEventHandler(
                SensorDataChangedEvent, self.__sensorDataChanged)
            super()._installEventHandler(
                ThermostatStateChangedEvent, self.__thermostatStateChanged)
            super()._installEventHandler(
                PowerPriceChangedEvent, self.__powerPriceChanged)
            super()._installEventHandler(
                SettingsChangedEvent, self.__processSettingsChanged)
        except:
            log.warning('Unable to connect to local influx instance')

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        self.__updateInflux(f'price={event.price}')

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        settings = self._getService(Settings)
        self.__updateInflux(
            f'comfortMin={settings.comfortMin},'
            f'comfortMax={settings.comfortMax}'
        )

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
        except Exception as e:
            log.warning("Failed connecting to influx")
            log.warning(str(e))
