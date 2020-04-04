import json
import requests
import json
import sys

from influxdb import InfluxDBClient
from threading import Thread

from src.logging import log
from src.core import ServiceProvider, Event, EventBus, EventBusMember, \
    ThermostatState
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent
from src.services import ConfigService, SettingsChangedEvent, SettingsService


class InfluxDataExporterService(EventBusMember):

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(ConfigService)
        if not config.resolve("influxdb", "enabled", False):
            raise RuntimeError('InfluxDB is not configured')

        self.__unitName = config.resolve('thermostat', 'unitname')
        self.__statusMeasurement = 'rpt_status'
        self.__eventMeasurement = 'rpt_event'
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

            self.__updateInflux(self.__eventMeasurement, "event=100")

            super()._installEventHandler(
                SensorDataChangedEvent, self.__sensorDataChanged)
            super()._installEventHandler(
                ThermostatStateChangedEvent, self.__thermostatStateChanged)
            super()._installEventHandler(
                PowerPriceChangedEvent, self.__powerPriceChanged)
            super()._installEventHandler(
                SettingsChangedEvent, self.__processSettingsChanged)
        except Exception:
            log.warning('Unable to connect to local influx instance')

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        self.__updateInflux(self.__statusMeasurement, f'price={event.price}')

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        settings = self._getService(SettingsService)
        self.__updateInflux(
            self.__statusMeasurement,
            f'comfortMin={settings.comfortMin},'
            f'comfortMax={settings.comfortMax}'
        )

    def __thermostatStateChanged(self, event: ThermostatStateChangedEvent):
        cool = 1 if ThermostatState.COOLING == event.state else 0
        heat = 1 if ThermostatState.HEATING == event.state else 0
        fan = 1 if ThermostatState.FAN == event.state else 0
        self.__updateInflux(
            self.__statusMeasurement,
            f'cool={cool},heat={heat},fan={fan}')

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        self.__updateInflux(
            self.__statusMeasurement,
            f'temperature={event.temperature},'
            f'pressure={event.pressure},'
            f'humidity={event.humidity}'
        )

    def __updateInflux(self, measurement: str, data: str):
        entry = f'{measurement},unit={self.__unitName} {data}'
        try:
            self.__client.write_points(entry, protocol=self.__protocol)
        except Exception as e:
            log.warning(f"Failed connecting to influx: {str(e)}")
