import os
import json
import configparser


class Config:

    def __init__(self):
        localPath = os.path.realpath(__file__)
        searchOrder = (
            os.path.expanduser('~/.thermostat.json'),
            '/etc/thermostat.json',
            os.path.dirname(localPath) + '/../etc/thermostat.json'
        )

        for fileName in searchOrder:
            if os.path.exists(fileName):
                with open(fileName) as configFile:
                    self.__config = json.load(configFile)
                break

    def __resolve(self, section, option, default=None):
        if section not in self.__config:
            raise RuntimeError(f'Section {section} is not in config file')
        if option in self.__config[section]:
            return self.__config[section][option]
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
        return self.__resolve('gogriddy', 'settlementPoint')

    @property
    def gogriddy_apiUrl(self):
        return self.__resolve('gogriddy', 'apiUrl')

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
        return self.__resolve('influxdb', 'dbName')

    @property
    def influxdb_protocol(self):
        return self.__resolve('influxdb', 'protocol')


config = Config()
