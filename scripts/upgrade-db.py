#!/usr/bin/python3

from sqlalchemy import text
import argparse

from src.services import OrmStateManagementService
from src.core import ServiceProvider, EventBus
from src.logging import handleException


class DatabaseUpgrader(ServiceProvider):

    def __init__(self):
        super().__init__()

        self.__eventBus = EventBus()
        self.installService(EventBus, self.__eventBus)

    def exec(self, finalize: bool):
        ormStateManagementService = OrmStateManagementService()
        session = ormStateManagementService.session

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
        ormStateManagementService.setServiceProvider(self)

        query = text("SELECT uid FROM thermostat")
        result = session.connection().execute(query)
        uidList = list(row[0] for row in result.fetchall())
        if len(uidList) != 1:
            raise RuntimeError("Encountered thermostat uid list != 1 entry")
        thermostatUid = uidList[0]

        query = text(
            "INSERT INTO version_info (time, major, minor) "
            "VALUES (now(), 1, 1)")
        result = session.connection().execute(query)

        query = text(
            f"INSERT INTO thermostat_state("
            f"    thermostat_uid, time, fan, cooling, heating) "
            f"SELECT "
            f"    {thermostatUid}, time, fan, cooling, heating "
            f"FROM rpt_old.thermostat_state")
        result = session.connection().execute(query)

        query = text(
            f"INSERT INTO thermostat_targets("
            f"    thermostat_uid, time, mode, comfort_min, comfort_max) "
            f"SELECT "
            f"    {thermostatUid}, time, mode, comfort_min, comfort_max "
            f"FROM rpt_old.thermostat_targets")
        result = session.connection().execute(query)

        query = text(
            f"INSERT INTO griddy_update("
            f"    thermostat_uid, time, price) "
            f"SELECT "
            f"    {thermostatUid}, time, price "
            f"FROM rpt_old.griddy_update")
        result = session.connection().execute(query)

        query = text(
            f"INSERT INTO sensor_reading("
            f"    thermostat_uid, time, temperature, pressure, humidity) "
            f"SELECT "
            f"    {thermostatUid}, time, temperature, pressure, humidity "
            f"FROM rpt_old.sensor_reading")
        result = session.connection().execute(query)

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

    try:
        upgrader = DatabaseUpgrader()
        upgrader.exec(args.finalize)
        exit(0)
    except:
        handleException("Failed upgrading")

    exit(1)
