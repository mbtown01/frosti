from collections import deque
from time import sleep
from queue import Queue
from threading import Thread

from src.settings import Settings
from src.events import FloatEvent, Event, EventBus, EventHandler


class TemperatureChangedEvent(FloatEvent):
    def __init__(self, value: float):
        super().__init__(value)


class PressureChangedEvent(FloatEvent):
    def __init__(self, value: float):
        super().__init__(value)


class HumidityChangedEvent(FloatEvent):
    def __init__(self, value: float):
        super().__init__(value)


class ThermostatDriver(EventHandler):
    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus)

        self.__settings = Settings()
        super()._subscribe(TemperatureChangedEvent, self.processTemperature)

    def processTemperature(self, event: TemperatureChangedEvent):
        temperature = event.getValue()

        # If we are over the temperature goal, enable the fan
        if temperature > self.__settings.getCoolThreshold():
            pass

        # If we are under the min temperature, disable the fan
        if temperature <= self.__settings.getHeatThreshold():
            pass
