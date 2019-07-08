from collections import deque
from time import sleep
from queue import Queue
from threading import Thread

from src.settings import Settings
from src.events import Event, EventType, FloatEvent, EventBus, EventHandler


class ThermostatDriver(EventHandler):
    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus)

        self.__settings = Settings()
        super()._subscribe(EventType.TEMPERATURE, self.processTemperature)

    def processTemperature(self, event: FloatEvent):
        temperature = event.getValue()
        print(f'Received {event.getType()} {temperature}')

        # If we are over the temperature goal, enable the fan
        if temperature > self.__settings.getCoolThreshold():
            pass

        # If we are under the min temperature, disable the fan
        if temperature <= self.__settings.getHeatThreshold():
            pass
