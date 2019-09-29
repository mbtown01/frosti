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

    def getJson(self):
        """ Gets the fully resolved json config data """
        return self.__config

    def resolve(self, section, option, default=None):
        """ Helper method for getting simple properties from json data """
        if section not in self.__config:
            raise RuntimeError(f'Section {section} is not in config file')
        if option in self.__config[section]:
            return self.__config[section][option]
        return default


config = Config()
