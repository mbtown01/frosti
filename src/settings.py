from enum import Enum

from src.events import Event, EventBus, EventHandler


class Mode(Enum):
    OFF = 0
    AUTO = 1
    COOL = 2
    HEAT = 3


class Settings:
    def __init__(self, mode=Mode.AUTO, min=68.0, max=75.0, delta=1.0):
        self.__comfortMin = min
        self.__comfortMax = max
        self.__delta = delta
        self.__mode = mode

    def __repr__(self):
        return f"[{self.__mode}] heatAt:{self.__comfortMin} " + \
               f"coolAt:{self.__comfortMax}"

    @property
    def comfortMin(self):
        return self.__comfortMin

    @property
    def comfortMax(self):
        return self.__comfortMax

    @property
    def delta(self):
        return self.__delta

    @property
    def mode(self):
        return self.__mode


class SettingsChangedEvent(Event):
    def __init__(self, settings: Settings):
        super().__init__('SettingsChangedEvent', {'settings': settings})

    @property
    def settings(self):
        return self._data['settings']
