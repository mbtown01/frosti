from enum import Enum


class Display:
    pass


class EventType(Enum):
    BUTTON_1 = 1
    BUTTON_2 = 2
    BUTTON_3 = 3
    BUTTON_4 = 4
    TEMPERATURE = 5
    PRESSURE = 6
    HUMIDITY = 7


class Event:
    def __init__(self, type: EventType, data: dict={}):
        self.__type = type
        self.__data = data

    def getType(self):
        return self.__type

    def getData(self):
        return self.__data.copy()


class FloatEvent(Event):
    def __init__(self, type: EventType, value: float):
        self.__value = value
        super().__init__(type, {'value': value})

    def getValue(self):
        return self.__value
