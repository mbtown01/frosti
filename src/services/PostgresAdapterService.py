import json
import requests
import json
import sys
import datetime

from sqlalchemy import create_engine, Column, Float, DateTime, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

from src.logging import log
from src.core import ServiceProvider, Event, EventBus, EventBusMember, \
    ThermostatState
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent
from src.services import ConfigService, SettingsChangedEvent, SettingsService


Base = declarative_base()


class Configuration(Base):
    ''' Basic configuration for the entire system, designed as a single row '''
    __tablename__ = 'configuration'

    id = Column(Integer, primary_key=True)
    ''' Total fluxuation around set point allowed before action '''
    delta = Column(Float)
    ''' Seconds to run the fan after heat/cool has ended '''
    fan_runout = Column(Integer)
    ''' Seconds to run the backlight on the LCD after last user input '''
    backlight_timeout = Column(Integer)


class SensorReading(Base):
    ''' All sensor readings at a specific date/time '''
    __tablename__ = 'sensor_reading'

    ''' Time of the reading '''
    time = Column(DateTime, primary_key=True, default=datetime.datetime.now)
    ''' Temperature in degF '''
    temperature = Column(Float)
    ''' Pressure in hPa (100 Pascals) '''
    pressure = Column(Float)
    ''' Humidity in relative percentage 0-99 '''
    humidity = Column(Float)

    def __init__(self, temperature: float, pressure: float, humidity: float):
        self.temperature = temperature
        self.pressure = pressure
        self.humidity = humidity


class GriddyConfig(Base):
    ''' Configuration for GoGriddy integration '''
    __tablename__ = 'griddy_config'

    ''' Centerpoint meter id '''
    meter_id = Column(String, primary_key=True)
    ''' Griddy member id '''
    member_id = Column(String)
    ''' ERCOT settlement point '''
    settlement_point = Column(String)
    ''' Griddy's API URL end point '''
    api_url = Column(String)


class Program(Base):
    ''' A user-named program defining thermostat behavior '''
    __tablename__ = 'program'

    name = Column(String, primary_key=True)
    comfort_min = Column(Float)
    comfort_max = Column(Float)


class PostgresAdapterService(EventBusMember):

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(ConfigService)

        self.__unitName = config.resolve('thermostat', 'unitname')
        self.__statusMeasurement = 'rpt_status'
        self.__eventMeasurement = 'rpt_event'
        self.__lastSensorChangedEvent = None
        self.__postgresUrl = 'postgresql://postgres:rpt@postgres/rpt'

        if not database_exists(self.__postgresUrl):
            create_database(self.__postgresUrl)

        self.__engine = create_engine(
            self.__postgresUrl, echo=False)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()

        connection = self.__engine.connect()
        Base.metadata.create_all(self.__engine)

        try:
            self.__updateDb(self.__eventMeasurement, {'event': 100})

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
        self.__updateDb(self.__statusMeasurement, {
            'price': event.price
        })

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        settings = self._getService(SettingsService)
        self.__updateDb(
            self.__statusMeasurement, {
                'comfortMin': settings.comfortMin,
                'comfortMax': settings.comfortMax
            }
        )

    def __thermostatStateChanged(self, event: ThermostatStateChangedEvent):
        self.__updateDb(
            self.__statusMeasurement, {
                'cool': 1 if ThermostatState.COOLING == event.state else 0,
                'heat': 1 if ThermostatState.HEATING == event.state else 0,
                'fan': 1 if ThermostatState.FAN == event.state else 0
            }
        )

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        reading = SensorReading(
            temperature=event.temperature,
            pressure=event.pressure,
            humidity=event.humidity
        )
        self.__session.add(reading)
        self.__session.commit()

    def __updateDb(self, table: str, data: dict):
        pass
        # entry = f'{measurement},unit={self.__unitName} {data}'
        # try:
        #     self.__client.write_points(entry, protocol=self.__protocol)
        # except Exception as e:
        #     log.warning(f"Failed connecting to influx: {str(e)}")
