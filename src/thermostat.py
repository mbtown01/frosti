from enum import Enum

from src.logging import log
from src.settings import settings, Settings, SettingsChangedEvent
from src.events import Event, EventBus, EventHandler


class ThermostatState(Enum):
    OFF = 0
    COOLING = 1
    HEATING = 2
    FAN = 3


class ThermostatStateChangedEvent(Event):
    def __init__(self, value: ThermostatState):
        super().__init__('ThermostatStateChangedEvent', {'state': value})

    @property
    def state(self):
        """ Returns the new state of the thermostat
        """
        return self._data['state']


class PropertyChangedEvent(Event):
    def __init__(self, name: str, value: float):
        super().__init__(name, {'value': value})

    @property
    def value(self):
        return float(self._data['value'])


class TemperatureChangedEvent(PropertyChangedEvent):
    def __init__(self, value: float):
        super().__init__('TemperatureChangedEvent', value)


class PressureChangedEvent(PropertyChangedEvent):
    def __init__(self, value: float):
        super().__init__('PressureChangedEvent', value)


class HumidityChangedEvent(PropertyChangedEvent):
    def __init__(self, value: float):
        super().__init__('HumidityChangedEvent', value)


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

    @property
    def state(self):
        return self.__state

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        log.debug(f"ThermostatDriver: new settings: {settings}")
        if settings.mode == Settings.Mode.OFF:
            self.__changeState(ThermostatState.OFF)

    def __processTemperatureChanged(self, event: TemperatureChangedEvent):
        if settings.mode == Settings.Mode.COOL:
            self.__processCooling(event.value)
        elif settings.mode == Settings.Mode.HEAT:
            self.__processHeating(event.value)
        elif settings.mode == Settings.Mode.AUTO:
            self.__processAuto(event.value)

    def __processCooling(self, newTemp: float):
        runAt = settings.comfortMax+settings.delta
        runUntil = settings.comfortMax-settings.delta

        if self.__state != ThermostatState.COOLING and newTemp > runAt:
            self.__changeState(ThermostatState.COOLING)
        elif newTemp <= runUntil:
            self.__changeState(ThermostatState.OFF)

    def __processHeating(self, newTemp: float):
        runAt = settings.comfortMin-settings.delta
        runUntil = settings.comfortMin+settings.delta

        if self.__state != ThermostatState.HEATING and newTemp < runAt:
            self.__changeState(ThermostatState.HEATING)
        elif newTemp >= runUntil:
            self.__changeState(ThermostatState.OFF)

    def __processAuto(self, newTemp: float):
        runAtHeat = settings.comfortMin-settings.delta
        runUntilHeat = settings.comfortMin+settings.delta
        runAtCool = settings.comfortMax+settings.delta
        runUntilCool = settings.comfortMax-settings.delta

        if self.__state != ThermostatState.COOLING and newTemp > runAtCool:
            self.__changeState(ThermostatState.COOLING)
        elif self.__state != ThermostatState.HEATING and newTemp < runAtHeat:
            self.__changeState(ThermostatState.HEATING)
        elif newTemp >= runUntilHeat and newTemp <= runUntilCool:
            self.__changeState(ThermostatState.OFF)

    def __changeState(self, newState: ThermostatState):
        self.__state = newState
        self._fireEvent(ThermostatStateChangedEvent(newState))
