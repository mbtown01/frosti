import os
import yaml


class ConfigService:
    """ Represents the configuration for the system.  Configuration includes
    the constant parameters used for operation plus default thermostat
    settings that get fed tothe SettingsService """

    def __init__(self, name: str='base', yamlData: str=None, data: dict={}):
        self.__name = name
        if len(data) > 0:
            self.__data = data
        elif yamlData is not None:
            self.__data = yaml.load(yamlData)
        else:
            localPath = os.path.realpath(__file__)

            searchOrder = (
                os.path.expanduser('~/.thermostat.yaml'),
                '/etc/thermostat.yaml',
                os.path.abspath(
                    os.path.dirname(localPath) + '/../../etc/thermostat.yaml')
            )

            self.__data = None
            for fileName in searchOrder:
                if os.path.exists(fileName):
                    self.__name = fileName
                    with open(fileName) as configFile:
                        self.__data = yaml.load(
                            configFile, Loader=yaml.FullLoader)
                    break

    def getData(self):
        """ Gets the fully resolved config data """
        return self.__data

    def resolve(self, section, option, default=None):
        """ Helper method for getting simple properties from the data """
        if section not in self.__data:
            raise RuntimeError(f'Section {section} is not in config file')
        if option in self.__data[section]:
            return self.__data[section][option]
        return default

    def value(self, section: str, default=None):
        if section not in self.__data:
            if default is None:
                raise RuntimeError(
                    f"'{self.__name}'' does not contain '{section}'")
            return default

        rtn = self.__data[section]
        if type(rtn) is dict:
            return ConfigService(name=f"{self.__name}::{section}", data=rtn)
        return rtn
