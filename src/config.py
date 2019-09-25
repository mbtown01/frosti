import os
import json
import configparser


class Config:

    def __init__(self):
        localPath = os.path.realpath(__file__)
        searchOrder = (
            os.path.expanduser('~/.thermostat.json'),
            '/etc/thermostat.json',
            os.path.abspath(
                os.path.dirname(localPath) + '/../etc/thermostat.json')
        )

        self.__config = None
        for fileName in searchOrder:
            if os.path.exists(fileName):
                with open(fileName) as configFile:
                    self.__config = json.load(configFile)
                break
        if self.__config is None:
            raise RuntimeError("No configuration was found")

    @property
    def json(self):
        return self.__config

    def resolve(self, section, option, default=None):
        """ Helper method for getting simple properties from json data """
        if section not in self.__config:
            raise RuntimeError(f'Section {section} is not in config file')
        if option in self.__config[section]:
            return self.__config[section][option]
        return default

    @property
    def gogriddy_enabled(self):
        return self.resolve('gogriddy', 'enabled', False)

    @property
    def gogriddy_memberId(self):
        return self.resolve('gogriddy', 'memberId')

    @property
    def gogriddy_meterId(self):
        return self.resolve('gogriddy', 'meterId')

    @property
    def gogriddy_settlementPoint(self):
        return self.resolve('gogriddy', 'settlementPoint')

    @property
    def gogriddy_apiUrl(self):
        return self.resolve('gogriddy', 'apiUrl')

    @property
    def influxdb_enabled(self):
        return self.resolve('influxdb', 'enabled', False)

    @property
    def influxdb_host(self):
        return self.resolve('influxdb', 'host')

    @property
    def influxdb_port(self):
        return self.resolve('influxdb', 'port')

    @property
    def influxdb_dbName(self):
        return self.resolve('influxdb', 'dbName')

    @property
    def influxdb_protocol(self):
        return self.resolve('influxdb', 'protocol')


config = Config()
