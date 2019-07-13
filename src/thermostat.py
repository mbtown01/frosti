from collections import deque
from time import sleep
from queue import Queue
from threading import Thread
from enum import Enum

from src.settings import Settings, SettingsChangedEvent, Mode
from src.events import Event, EventBus, EventHandler


class ThermostatState(Enum):
    OFF = 0
    COOLING = 1
    HEATING = 2
    FAN = 3


class ThermostatStateChangedEvent(Event):
    def __init__(self, value: ThermostatState):
        super().__init__({'state': value})

    @property
    def state(self):
        """ Returns the new state of the thermostat
        """
        return self._data['state']


class PropertyChangedEvent(Event):
    def __init__(self, value: float):
        super().__init__({'value': value})

    @property
    def value(self):
        return float(self._data['value'])


class TemperatureChangedEvent(PropertyChangedEvent):
    def __init__(self, value: float):
        super().__init__(value)


class PressureChangedEvent(PropertyChangedEvent):
    def __init__(self, value: float):
        super().__init__(value)


class HumidityChangedEvent(PropertyChangedEvent):
    def __init__(self, value: float):
        super().__init__(value)


class ThermostatDriver(EventHandler):
    """ Thermostat driver logic
    """

    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus)
        super()._subscribe(
            SettingsChangedEvent, self.__processSettingsChanged)
        super()._subscribe(
            TemperatureChangedEvent, self.__processTemperatureChanged)

        self.__state = ThermostatState.OFF
        self.__settings = None

    @property
    def state(self):
        return self.__state

    @property
    def settings(self):
        return self.__settings

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        print(f"ThermostatDriver: new settings: {event.settings}")
        self.__settings = event.settings

    def __processTemperatureChanged(self, event: TemperatureChangedEvent):
        if self.__settings is None:
            raise RuntimeError("Temperature event received before settings")

        if self.__settings.mode == Mode.COOL:
            self.__processCooling(event.value)
        elif self.__settings.mode == Mode.HEAT:
            self.__processHeating(event.value)
        elif self.__settings.mode == Mode.AUTO:
            self.__processCooling(event.value)
            self.__processHeating(event.value)

    def __processCooling(self, temperature: float):
        runAt = self.__settings.comfortMax+self.__settings.delta
        runUntil = self.__settings.comfortMax-self.__settings.delta

        if self.state != ThermostatState.COOLING and temperature > runAt:
            self.__changeState(ThermostatState.COOLING)
        if self.state == ThermostatState.COOLING and temperature <= runUntil:
            self.__changeState(ThermostatState.OFF)

    def __processHeating(self, temperature: float):
        runAt = self.__settings.comfortMin-self.__settings.delta
        runUntil = self.__settings.comfortMin+self.__settings.delta

        if self.state != ThermostatState.HEATING and temperature < runAt:
            self.__changeState(ThermostatState.HEATING)
        if self.state == ThermostatState.HEATING and temperature >= runUntil:
            self.__changeState(ThermostatState.OFF)

    def __changeState(self, newState: ThermostatState):
        self.__state = newState
        self._fireEvent(ThermostatStateChangedEvent(newState))
