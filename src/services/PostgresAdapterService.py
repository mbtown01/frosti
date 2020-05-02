from sqlalchemy import create_engine, Column, Float, DateTime, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.sql import func

from .SettingsService import SettingsService, SettingsChangedEvent
from src.logging import log
from src.core import ServiceProvider, ServiceConsumer, EventBus, \
    ThermostatState
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent


Base = declarative_base()


class OrmConfiguration(Base):
    ''' Basic configuration for the entire system, designed as a single row '''
    __tablename__ = 'configuration'

    id = Column(Integer, primary_key=True)
    ''' Total fluxuation around set point allowed before action '''
    delta = Column(Float)
    ''' Seconds to run the fan after heat/cool has ended '''
    fan_runout = Column(Integer)
    ''' Seconds to run the backlight on the LCD after last user input '''
    backlight_timeout = Column(Integer)


class OrmGriddyConfig(Base):
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


class OrmProgram(Base):
    ''' A user-named program defining thermostat behavior '''
    __tablename__ = 'program'

    name = Column(String, primary_key=True)
    ''' Minimum temperature before heat is engaged '''
    comfort_min = Column(Float)
    ''' Maximum temperature before air conditioning is engaged '''
    comfort_max = Column(Float)


class OrmSensorReading(Base):
    ''' All sensor readings at a specific date/time '''
    __tablename__ = 'sensor_reading'

    ''' Time of the reading '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())
    ''' Temperature in degF '''
    temperature = Column(Float)
    ''' Pressure in hPa (100 Pascals) '''
    pressure = Column(Float)
    ''' Humidity in relative percentage 0-99 '''
    humidity = Column(Float)


class OrmThermostatState(Base):
    __tablename__ = 'thermostat_state'

    ''' Time of the event '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())
    fan = Column(Integer)
    cooling = Column(Integer)
    heating = Column(Integer)


class OrmThermostatTargets(Base):
    __tablename__ = 'thermostat_targets'

    ''' Time of the event '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())
    mode = Column(Integer)
    ''' Minimum temperature before heat is engaged '''
    comfort_min = Column(Float)
    ''' Maximum temperature before air conditioning is engaged '''
    comfort_max = Column(Float)


class OrmGriddyUpdate(Base):
    __tablename__ = 'griddy_update'

    ''' Time of the event '''
    time = Column(
        DateTime(timezone=True), primary_key=True, default=func.now())
    ''' Current price '''
    price = Column(Float)


class PostgresAdapterService(ServiceConsumer):
    MODE_CODES = {
        SettingsService.Mode.OFF: 0x00,
        SettingsService.Mode.FAN: 0x01,
        SettingsService.Mode.HEAT: 0x03,
        SettingsService.Mode.COOL: 0x05,
        SettingsService.Mode.AUTO: 0x07
    }

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        self.__postgresUrl = 'postgresql://rpt:rpt@postgres/rpt'
        if not database_exists(self.__postgresUrl):
            create_database(self.__postgresUrl)
        self.__engine = create_engine(self.__postgresUrl, echo=False)
        Session = sessionmaker(bind=self.__engine)
        self.__session = Session()
        self.__connection = self.__engine.connect()

        Base.metadata.create_all(self.__engine)

        try:
            eventBus = self._getService(EventBus)
            eventBus.installEventHandler(
                SensorDataChangedEvent, self.__sensorDataChanged)
            eventBus.installEventHandler(
                ThermostatStateChangedEvent, self.__thermostatStateChanged)
            eventBus.installEventHandler(
                PowerPriceChangedEvent, self.__powerPriceChanged)
            eventBus.installEventHandler(
                SettingsChangedEvent, self.__processSettingsChanged)
        except Exception:
            log.warning('Unable to connect to local influx instance')

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        entity = OrmGriddyUpdate()
        entity.price = event.price

        self.__session.add(entity)
        self.__session.commit()

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        settings = self._getService(SettingsService)

        entity = OrmThermostatTargets()
        entity.mode = self.MODE_CODES[settings.mode]
        entity.comfort_max = settings.comfortMax
        entity.comfort_min = settings.comfortMin

        self.__session.add(entity)
        self.__session.commit()

    def __thermostatStateChanged(self, event: ThermostatStateChangedEvent):
        entity = OrmThermostatState()
        entity.cooling = 1 if ThermostatState.COOLING == event.state else 0
        entity.heating = 1 if ThermostatState.HEATING == event.state else 0
        entity.fan = 1 if ThermostatState.FAN == event.state else 0

        self.__session.add(entity)
        self.__session.commit()

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        entity = OrmSensorReading()
        entity.temperature = event.temperature
        entity.pressure = event.pressure
        entity.humidity = event.humidity

        self.__session.add(entity)
        self.__session.commit()
