#!/usr/bin/python3

from sqlalchemy import text
import argparse

from src.services import OrmManagementService, ConfigService
from src.core import ServiceProvider, EventBus
from src.logging import handleException, setupLogging
from src.core.orm import OrmSchedule, OrmProgram, OrmScheduleDay, \
    OrmScheduleTime, OrmPriceOverride


class DatabaseUpgrader(ServiceProvider):

    def __init__(self):
        super().__init__()

        self.installService(EventBus, EventBus())
        self.installService(ConfigService, ConfigService())

    def exec(self, finalize: bool):
        ormManagementService = OrmManagementService()
        session = ormManagementService.session

        # Take the existing schema and rename it to rpt_old, but keep
        # all the data so we can move it over
        query = text("SELECT schema_name FROM information_schema.schemata")
        result = session.connection().execute(query)
        nameList = list(row[0] for row in result.fetchall())
        if 'rpt_old' not in nameList:
            session.connection().execute(
                'ALTER SCHEMA public RENAME TO rpt_old')
        else:
            session.connection().execute('DROP SCHEMA public CASCADE')
        session.connection().execute('CREATE SCHEMA public')
        session.commit()

        # This establishes the new schema in 'public'
        ormManagementService.setServiceProvider(self)

        query = text(
            "INSERT INTO version_info (time, major, minor) "
            "VALUES (now(), 1, 1)")
        result = session.connection().execute(query)

        query = text(
            "INSERT INTO thermostat_state("
            "    time, fan, cooling, heating) "
            "SELECT "
            "    time, fan, cooling, heating "
            "FROM rpt_old.thermostat_state")
        result = session.connection().execute(query)

        query = text(
            "INSERT INTO thermostat_targets("
            "    time, mode, comfort_min, comfort_max) "
            "SELECT "
            "    time, mode, comfort_min, comfort_max "
            "FROM rpt_old.thermostat_targets")
        result = session.connection().execute(query)

        query = text(
            "INSERT INTO griddy_update("
            "    time, price) "
            "SELECT "
            "    time, price "
            "FROM rpt_old.griddy_update")
        result = session.connection().execute(query)

        query = text(
            "INSERT INTO sensor_reading("
            "    time, temperature, pressure, humidity) "
            "SELECT "
            "    time, temperature, pressure, humidity "
            "FROM rpt_old.sensor_reading")
        result = session.connection().execute(query)

        configService = self.getService(ConfigService)
        thermostatData = configService.getData().get('thermostat', dict())
        programData = thermostatData.get('programs', dict())
        for name, pData in programData.items():
            program = OrmProgram()
            program.name = name
            program.comfort_min = pData.get('comfortMin', 68)
            program.comfort_max = pData.get('comfortMax', 78)
            session.add(program)
            for oData in pData.get('priceOverrides', list()):
                priceOverride = OrmPriceOverride()
                priceOverride.program_name = name
                priceOverride.price = oData['price']
                priceOverride.comfort_min = oData.get('comfortMin', 68)
                priceOverride.comfort_max = oData.get('comfortMax', 78)
                session.add(priceOverride)

        scheduleData = thermostatData.get('schedule', dict())
        for name, sData in scheduleData.items():
            schedule = OrmSchedule()
            schedule.name = name
            session.add(schedule)
            for day in sData.get('days', list()):
                scheduleDay = OrmScheduleDay()
                scheduleDay.schedule_name = name
                scheduleDay.day = day
                session.add(scheduleDay)
            for tData in sData.get('times', list()):
                scheduleTime = OrmScheduleTime()
                scheduleTime.schedule_name = name
                scheduleTime.program_name = tData['program']
                scheduleTime.hour = tData['hour']
                scheduleTime.minute = tData['minute']
                session.add(scheduleTime)

        session.commit()

        if finalize:
            session.connection().execute('DROP SCHEMA rpt_old CASCADE')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='RPT database upgrade tool')
    parser.add_argument(
        '--finalize', default=False, action='store_true',
        help='Drop the backup schema when complete')
    args = parser.parse_args()

    setupLogging()

    try:
        upgrader = DatabaseUpgrader()
        upgrader.exec(args.finalize)
    except:
        handleException("Failed upgrading")
