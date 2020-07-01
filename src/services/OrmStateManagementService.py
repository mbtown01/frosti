from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
import os
import yaml

from .SettingsService import SettingsService, SettingsChangedEvent
from src.logging import handleException
from src.core import ServiceProvider, ServiceConsumer, EventBus, \
    ThermostatState
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent
from src.core.orm import OrmSensorReading, OrmThermostatState, \
    OrmThermostatTargets, OrmGriddyUpdate, OrmThermostat, OrmGriddyConfig, \
    Base
from src.logging import log

DB_URL_RPT = 'postgresql://rpt:rpt@postgres/rpt'


class OrmStateManagementService(ServiceConsumer):
    MODE_CODES = {
        SettingsService.Mode.OFF: 0x00,
        SettingsService.Mode.FAN: 0x01,
        SettingsService.Mode.HEAT: 0x03,
        SettingsService.Mode.COOL: 0x05,
        SettingsService.Mode.AUTO: 0x07
    }

    def __init__(self):
        self.__engine = create_engine(DB_URL_RPT, echo=False)
        self.__session = sessionmaker(bind=self.__engine)()
        self.__connection = self.__engine.connect()

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        Base.metadata.create_all(self.__engine)

        thermostatEntries = list(
            self.__session.query(OrmThermostat).filter_by(name='DEFAULT'))
        if len(thermostatEntries) != 1:
            self.__initializeThermostat()
        else:
            self.__thermostat = thermostatEntries[0]

        eventBus = self._getService(EventBus)
        eventBus.installEventHandler(
            SensorDataChangedEvent, self.__sensorDataChanged)
        eventBus.installEventHandler(
            ThermostatStateChangedEvent, self.__thermostatStateChanged)
        eventBus.installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)
        eventBus.installEventHandler(
            SettingsChangedEvent, self.__processSettingsChanged)

    @property
    def session(self):
        return self.__session

    def __initializeThermostat(self):
        try:
            localPath = os.path.realpath(__file__)

            searchOrder = (
                os.path.expanduser('~/.thermostat.yaml'),
                '/etc/thermostat.yaml',
                os.path.abspath(
                    os.path.dirname(localPath) + '/../../etc/thermostat.yaml')
            )

            self.__data = None
            for fileName in searchOrder:
                if os.path.exists(fileName):
                    self.__name = fileName
                    log.info(f"Configuration coming from {self.__name}")
                    with open(fileName) as configFile:
                        self.__data = yaml.load(
                            configFile, Loader=yaml.FullLoader)
                    break

            thermostatData = self.__data.get('thermostat', {})
            thermostat = OrmThermostat()
            thermostat = OrmThermostat()
            thermostat.name = "DEFAULT"
            thermostat.delta = float(
                thermostatData.get('delta', '1.0'))
            thermostat.fan_runout = int(
                thermostatData.get('fan_runout', '30'))
            thermostat.backlight_timeout = int(
                thermostatData.get('backlight_timeout', '5'))
            self.__session.add(thermostat)
            self.__thermostat = thermostat

            self.__thermostat.griddy_config = None
            if 'gogriddy' in self.__data:
                griddyConfigData = self.__data['gogriddy']
                entity = OrmGriddyConfig()
                entity.thermostat_uid = self.__thermostat.uid
                entity.meter_id = griddyConfigData['meterID']
                entity.member_id = griddyConfigData['memberID']
                entity.api_url = griddyConfigData['apiUrl']
                entity.settlement_point = \
                    griddyConfigData['settlementPoint']
                self.__session.add(entity)
                self.__thermostat.griddy_config = entity

            self.__session.commit()
        except:
            handleException("Setup griddy data integration")

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        entity = OrmGriddyUpdate()
        entity.thermostat_uid = self.__thermostat.uid
        entity.price = event.price

        self.__session.add(entity)
        self.__session.commit()

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        settings = self._getService(SettingsService)

        entity = OrmThermostatTargets()
        entity.thermostat_uid = self.__thermostat.uid
        entity.mode = self.MODE_CODES[settings.mode]
        entity.comfort_max = settings.comfortMax
        entity.comfort_min = settings.comfortMin

        self.__session.add(entity)
        self.__session.commit()

    def __thermostatStateChanged(self, event: ThermostatStateChangedEvent):
        entity = OrmThermostatState()
        entity.thermostat_uid = self.__thermostat.uid
        entity.cooling = 1 if ThermostatState.COOLING == event.state else 0
        entity.heating = 1 if ThermostatState.HEATING == event.state else 0
        entity.fan = 1 if ThermostatState.FAN == event.state else 0

        self.__session.add(entity)
        self.__session.commit()

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        entity = OrmSensorReading()
        entity.thermostat_uid = self.__thermostat.uid
        entity.temperature = event.temperature
        entity.pressure = event.pressure
        entity.humidity = event.humidity

        self.__session.add(entity)
        self.__session.commit()
