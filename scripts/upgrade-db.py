#!/usr/bin/python3

from sqlalchemy import text
import argparse

from frosti.services import OrmManagementService
from frosti.core import ServiceProvider, EventBus
from frosti.logging import handleException, setupLogging


class DatabaseUpgrader(ServiceProvider):

    def __init__(self):
        super().__init__()

        self.installService(EventBus, EventBus())

    def exec(self, finalize: bool):
        ormManagementService = OrmManagementService()
        session = ormManagementService.session

        # Take the existing schema and rename it to frosti_old, but keep
        # all the data so we can move it over
        query = text("SELECT schema_name FROM information_schema.schemata")
        result = session.connection().execute(query)
        nameList = list(row[0] for row in result.fetchall())
        if 'frosti_old' not in nameList:
            session.connection().execute(
                'ALTER SCHEMA public RENAME TO frosti_old')
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
            "FROM frosti_old.thermostat_state")
        result = session.connection().execute(query)

        query = text(
            "INSERT INTO thermostat_targets("
            "    time, mode, comfort_min, comfort_max) "
            "SELECT "
            "    time, mode, comfort_min, comfort_max "
            "FROM frosti_old.thermostat_targets")
        result = session.connection().execute(query)

        query = text(
            "INSERT INTO griddy_update("
            "    time, price) "
            "SELECT "
            "    time, price "
            "FROM frosti_old.griddy_update")
        result = session.connection().execute(query)

        query = text(
            "INSERT INTO sensor_reading("
            "    time, temperature, pressure, humidity) "
            "SELECT "
            "    time, temperature, pressure, humidity "
            "FROM frosti_old.sensor_reading")
        result = session.connection().execute(query)

        session.commit()

        if finalize:
            session.connection().execute('DROP SCHEMA frosti_old CASCADE')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='FROSTI database upgrade tool')
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
