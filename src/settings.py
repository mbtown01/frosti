from enum import Enum


class Mode(Enum):
    OFF = 0
    AUTO = 1
    COOL = 2
    HEAT = 3


class Settings:
    def __init__(self, mode=Mode.AUTO, heat=68.0, cool=75.0, delta=1.0):
        self.__heatThreshold = heat
        self.__coolThreshold = cool
        self.__delta = delta
        self.__mode = mode

    def getHeatThreshold(self):
        return self.__heatThreshold

    def getCoolThreshold(self):
        return self.__coolThreshold

    def getDelta(self):
        return self.__delta

    def getMode(self):
        return self.__mode
