from sqlalchemy import create_engine, text
from sqlalchemy_utils.functions import database_exists
from sqlalchemy.orm import sessionmaker
import yaml

from .ConfigService import ConfigService
from src.logging import handleException
from src.core import ServiceProvider, ServiceConsumer
from src.core.orm import OrmThermostat, Base, OrmProgram, OrmSchedule, \
    OrmPriceOverride, OrmScheduleDay, OrmScheduleTime

DB_URL_TEMPLATE = 'postgresql://rpt:rpt@postgres/template1'
DB_URL_RPT_RUN = 'postgresql://rpt:rpt@postgres/rpt'
DB_URL_RPT_TEST = 'postgresql://rpt:rpt@postgres/rpt_test'


class OrmManagementService(ServiceConsumer):

    def __init__(self, isTestInstance: bool = False):
        url = DB_URL_RPT_TEST if isTestInstance else DB_URL_RPT_RUN
        if not database_exists(url):
            name = 'rpt_test' if isTestInstance else 'rpt'
            engine = create_engine(
                DB_URL_TEMPLATE, isolation_level='AUTOCOMMIT')
            session = sessionmaker(bind=engine)()
            session.execute(f'CREATE DATABASE {name}')

        self.__engine = create_engine(url, echo=False)
        self.__session = sessionmaker(bind=self.__engine)()
        self.__connection = self.__engine.connect()

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        Base.metadata.create_all(self.__engine)

        thermostatEntries = list(
            self.__session.query(OrmThermostat).filter_by(name='DEFAULT'))
        if len(thermostatEntries) != 1:
            self.__initializeDatabase()

    @property
    def session(self):
        ''' Returns the currently active SqlAlchemy session '''
        return self.__session

    @property
    def thermostat(self):
        ''' Returns the currently configured Thermostat '''
        thermostats = \
            list(self.__session.query(OrmThermostat))
        if len(thermostats) != 1:
            raise RuntimeError(f"Found {len(thermostats)} in OrmThermostat")
        return thermostats[0]

    def importFromYaml(self, yamlData: str):
        data = yaml.load(yamlData)

        tables = ['price_override', 'schedule_day', 'schedule_time',
                  'schedule', 'program']
        for tableName in tables:
            query = text(f"DELETE FROM {tableName} CASCADE")
            self.__session.connection().execute(query)

        thermostatData = data.get('thermostat', dict())
        programData = thermostatData.get('programs', dict())
        for name, pData in programData.items():
            program = OrmProgram()
            program.name = name
            program.comfort_min = pData.get('comfortMin', 68)
            program.comfort_max = pData.get('comfortMax', 78)
            self.__session.add(program)
            for oData in pData.get('priceOverrides', list()):
                priceOverride = OrmPriceOverride()
                priceOverride.program_name = name
                priceOverride.price = oData['price']
                priceOverride.comfort_min = oData.get('comfortMin', 68)
                priceOverride.comfort_max = oData.get('comfortMax', 78)
                self.__session.add(priceOverride)

        scheduleData = thermostatData.get('schedule', dict())
        for name, sData in scheduleData.items():
            schedule = OrmSchedule()
            schedule.name = name
            self.__session.add(schedule)
            for day in sData.get('days', list()):
                scheduleDay = OrmScheduleDay()
                scheduleDay.schedule_name = name
                scheduleDay.day = day
                self.__session.add(scheduleDay)
            for tData in sData.get('times', list()):
                scheduleTime = OrmScheduleTime()
                scheduleTime.schedule_name = name
                scheduleTime.program_name = tData['program']
                scheduleTime.hour = tData['hour']
                scheduleTime.minute = tData['minute']
                self.__session.add(scheduleTime)

        self.__session.commit()

    def __initializeDatabase(self):
        try:
            configService = self._getService(ConfigService)
            thermostatData = configService.getData().get('thermostat', {})
            thermostat = OrmThermostat()
            thermostat.name = "DEFAULT"
            thermostat.delta = float(
                thermostatData.get('delta', '1.0'))
            thermostat.fan_runout = int(
                thermostatData.get('fanRunout', '30'))
            thermostat.backlight_timeout = int(
                thermostatData.get('backlightTimeout', '5'))

            griddyConfigData = configService.getData().get('gogriddy', None)
            if griddyConfigData is not None:
                thermostat.meter_id = griddyConfigData['meterID']
                thermostat.member_id = griddyConfigData['memberID']
                thermostat.settlement_point = \
                    griddyConfigData['settlementPoint']

            self.__session.add(thermostat)
            self.__session.commit()
        except:
            handleException("Setup griddy data integration")
