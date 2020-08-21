from sqlalchemy import create_engine
from sqlalchemy_utils.functions import database_exists
from sqlalchemy.orm import sessionmaker

from src.core import ServiceProvider, ServiceConsumer
from src.core.orm import OrmConfig, Base

DB_URL_TEMPLATE = 'postgresql://rpt:rpt@postgres/template1'
DB_URL_RPT_RUN = 'postgresql://rpt:rpt@postgres/rpt'
DB_URL_RPT_TEST = 'postgresql://rpt:rpt@postgres/rpt_test'
DB_VERSION = 'v1.2'


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

        # Ensure the DB version agrees with the code version.  If for some
        # reason the database doesn't have a version, assume it's current and
        # then set it properly
        dbVersion = None
        for configEntry in self.__session.query(OrmConfig). \
                filter(OrmConfig.name == 'db.version'):
            dbVersion = configEntry.value
        if dbVersion is None:
            configEntry = OrmConfig()
            configEntry.name = 'db.version'
            configEntry.value = DB_VERSION
            dbVersion = DB_VERSION
            self.__session.add(configEntry)
            self.__session.commit()

        if DB_VERSION != dbVersion:
            raise RuntimeError('Database needs upgraded')

    @property
    def session(self):
        ''' Returns the currently active SqlAlchemy session '''
        return self.__session

    def getConfigString(self, name: str, default: str = None):
        ''' Returns a configuration value for a given name '''
        for configEntry in self.__session.query(OrmConfig). \
                filter(OrmConfig.name == name):
            return configEntry.value

        raise RuntimeError(f'Config key "{name}" is not defined')

    def getConfigInt(self, name: str, default: str = None):
        ''' Convenience method for getting a configuration value as int '''
        value = self.getConfigString(name, default)
        return int(value)

    def getConfigFloat(self, name: str, default: str = None):
        ''' Convenience method for getting a configuration value as float '''
        value = self.getConfigString(name, default)
        return float(value)
