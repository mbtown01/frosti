from enum import Enum

from src.events import Event, EventBus, EventHandler


class Mode(Enum):
    OFF = 0
    AUTO = 1
    COOL = 2
    HEAT = 3


class Settings:
    """ Captures the settings for the thermostat.  Settings are changed
    by the user during normal thermostat operation, and an event is
    fired when they are changed.
    """

    def __init__(self, mode=Mode.AUTO, min=68.0, max=75.0, delta=1.0):
        self.__comfortMin = min
        self.__comfortMax = max
        self.__delta = delta
        self.__mode = mode

    def __repr__(self):
        return f"[{self.__mode}] heatAt: {self.__comfortMin} " + \
               f"coolAt: {self.__comfortMax}"

    @property
    def comfortMin(self):
        """ Minimum temperature that is comfortable, anything lower
        and outside the delta needs the thermostat to heat
        """
        return self.__comfortMin

    @property
    def comfortMax(self):
        """ Maximum temperature that is comfortable, anything higher
        and outside the delta needs the thermostat to cool
        """
        return self.__comfortMax

    @property
    def delta(self):
        """ Temperate span above/below min/max the thermostat needs
        to heat/cool before it should stop
        """
        return self.__delta

    @property
    def mode(self):
        """ The current mode the thermostat is in
        """
        return self.__mode


class SettingsChangedEvent(Event):
    def __init__(self, settings: Settings):
        super().__init__('SettingsChangedEvent', {'settings': settings})

    @property
    def settings(self):
        return self._data['settings']
