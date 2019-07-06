from collections import deque
from time import sleep
from queue import Queue
from threading import Thread

from settings import Settings
from interfaces import Event, EventType, FloatEvent


class Driver:
    def __init__(self, settings: Settings):
        self.__settings = settings

        self.__eventHandlers = {}
        for eventType in EventType:
            self.__eventHandlers[eventType] = self.processUnhandled
        self.__eventHandlers[EventType.TEMPERATURE] = self.processTemperature
        self.__eventHandlers[EventType.PRESSURE] = self.processFloat
        self.__eventHandlers[EventType.HUMIDITY] = self.processFloat

    def processUnhandled(self, event: Event):
        print(f'Received unhandled {event.getType()}')

    def processFloat(self, event: FloatEvent):
        value = event.getValue()
        print(f'Received {event.getType()} {value}')

    def processTemperature(self, event: FloatEvent):
        temperature = event.getValue()
        print(f'Received {event.getType()} {temperature}')

        # If we are over the temperature goal, enable the fan
        if temperature > self.__settings.getCoolThreshold():
            pass

        # If we are under the min temperature, disable the fan
        if temperature <= self.__settings.getHeatThreshold():
            pass

    def exec(self, controlQueue: Queue, eventQueue: Queue):
        while True:
            event = eventQueue.get()
            self.__eventHandlers[event.getType()](event)
