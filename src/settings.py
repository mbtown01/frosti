from enum import Enum

from src.events import Event, EventBus, EventHandler
from src.logging import log


class SettingsChangedEvent(Event):
    def __init__(self):
        super().__init__('SettingsChangedEvent')


class Settings:
    """ Captures the settings for the thermostat.  Settings are changed
    by the user during normal thermostat operation, and an event is
    fired when they are changed.
    """

    class Mode(Enum):
        OFF = 0
        AUTO = 1
        COOL = 2
        HEAT = 3

    def __init__(self, mode: Mode=None,
                 comfortMin: float=None, comfortMax: float=None,
                 delta: float=None):
        self.__eventBus = None
        self.__comfortMin = comfortMin or 68.0
        self.__comfortMax = comfortMax or 75.0
        self.__delta = delta or 1.0
        self.__mode = mode or Settings.Mode.AUTO
        if self.__comfortMax - self.__comfortMin < 2*self.__delta:
            self.__comfortMax = self.__comfortMin + 2*self.__delta

    # def clone(self, mode: Mode=None,
    #           comfortMin: float=None, comfortMax: float=None,
    #           delta: float=None):

    #     return Settings(
    #         comfortMin=comfortMin or self.__comfortMin,
    #         comfortMax=comfortMax or self.__comfortMax,
    #         delta=delta or self.__delta,
    #         mode=mode or self.__mode
    #     )

    def __repr__(self):
        return f"[{self.__mode}] heatAt: {self.__comfortMin} " + \
               f"coolAt: {self.__comfortMax}"

    @property
    def comfortMin(self):
        """ Minimum temperature that is comfortable, anything lower
        and outside the delta needs the thermostat to heat
        """
        return self.__comfortMin

    @comfortMin.setter
    def comfortMin(self, value):
        self.__comfortMin = value
        if self.__eventBus is not None:
            self.__eventBus.put(SettingsChangedEvent())

    @property
    def comfortMax(self):
        """ Maximum temperature that is comfortable, anything higher
        and outside the delta needs the thermostat to cool
        """
        return self.__comfortMax

    @comfortMax.setter
    def comfortMax(self, value):
        self.__comfortMax = value
        if self.__eventBus is not None:
            self.__eventBus.put(SettingsChangedEvent())

    @property
    def delta(self):
        """ Temperate span above/below min/max the thermostat needs
        to heat/cool before it should stop
        """
        return self.__delta

    @delta.setter
    def delta(self, value):
        self.__delta = value
        if self.__eventBus is not None:
            self.__eventBus.put(SettingsChangedEvent())

    @property
    def mode(self):
        """ The current mode the thermostat is in
        """
        return self.__mode

    @mode.setter
    def mode(self, value):
        self.__mode = value
        if self.__eventBus is not None:
            self.__eventBus.put(SettingsChangedEvent())

    def setEventBus(self, eventBus: EventBus):
        """ Send SettingsChangedEvent notifications to the provided event bus,
        or nowhere if eventBus is None
        """
        self.__eventBus = eventBus

settings = Settings()
