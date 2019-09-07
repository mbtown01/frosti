import os
import configparser


class ThermostatConfig:

    def __init__(self):
        localPath = os.path.realpath(__file__)
        searchOrder = (
            os.path.dirname(localPath) + '/../etc/thermostat.conf',
            '/etc/thermostat.conf',
            os.path.expanduser('~/.thermostat.conf')
        )

        self.__config = configparser.ConfigParser()
        for dirName in searchOrder:
            if os.path.exists(dirName):
                self.__config.read(dirName)

    def __resolve(self, section, option, default=None):
        if self.__config.has_option(section, option):
            return self.__config.get(section, option)
        return default

    @property
    def gogriddy_enabled(self):
        return self.__resolve('gogriddy', 'enabled', False)

    @property
    def gogriddy_memberId(self):
        return self.__resolve('gogriddy', 'memberId')

    @property
    def gogriddy_meterId(self):
        return self.__resolve('gogriddy', 'meterId')

    @property
    def gogriddy_settlementPoint(self):
        return self.__resolve('gogriddy', 'settlement_point')

    @property
    def gogriddy_apiUrl(self):
        return self.__resolve('gogriddy', 'api_url')

    @property
    def influxdb_enabled(self):
        return self.__resolve('influxdb', 'enabled', False)

    @property
    def influxdb_host(self):
        return self.__resolve('influxdb', 'host')

    @property
    def influxdb_port(self):
        return self.__resolve('influxdb', 'port')

    @property
    def influxdb_dbName(self):
        return self.__resolve('influxdb', 'dbname')

    @property
    def influxdb_protocol(self):
        return self.__resolve('influxdb', 'protocol')


config = ThermostatConfig()
