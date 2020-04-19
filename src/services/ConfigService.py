import os
import json
import configparser


class ConfigService:
    """ Represents the configuration for the system.  Configuration includes
    the constant parameters used for operation plus default thermostat
    settings that get fed tothe SettingsService """

    def __init__(self, name: str = None, json: dict = {}):
        if name is None:
            self.__initFromEnviornment()
        else:
            self.__name = name
            self.__json = json

    def __initFromEnviornment(self):
        localPath = os.path.realpath(__file__)
        searchOrder = (
            os.path.expanduser('~/.thermostat.json'),
            '/etc/thermostat.json',
            os.path.abspath(
                os.path.dirname(localPath) + '/../../etc/thermostat.json')
        )

        self.__json = None
        for fileName in searchOrder:
            if os.path.exists(fileName):
                self.__name = fileName
                with open(fileName) as configFile:
                    self.__json = json.load(configFile)
                break
        if self.__json is None:
            raise RuntimeError("No configuration was found")
        if 'thermostat' not in self.__json:
            raise RuntimeError("No 'thermostat' section was found in config")

        if 'unitname' not in self.__json['thermostat']:
            self.__json['thermostat']['unitname'] = \
                os.environ.get('UNITNAME', 'test')

    def getJson(self):
        """ Gets the fully resolved json config data """
        return self.__json

    def resolve(self, section, option, default=None):
        """ Helper method for getting simple properties from json data """
        if section not in self.__json:
            raise RuntimeError(f'Section {section} is not in config file')
        if option in self.__json[section]:
            return self.__json[section][option]
        return default

    def value(self, section: str, default=None):
        if section not in self.__json:
            if default is None:
                raise RuntimeError(
                    f"'{self.__name}'' does not contain '{section}'")
            return default

        rtn = self.__json[section]
        if type(rtn) is dict:
            return ConfigService(name=f"{self.__name}::{section}", json=rtn)
        return rtn
