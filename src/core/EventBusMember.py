from queue import Queue
from threading import Event as ThreadingEvent
from sys import exc_info, maxsize
from time import time

from src.logging import log
from . import ServiceProvider, ServiceConsumer, Event, EventBus


class EventBusMember(ServiceConsumer):
    """ Helper base class for service consumers that are event bus aware """

    def __init__(self):
        self.__eventBus = None

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)
        self.__eventBus = self._getService(EventBus)

    def _fireEvent(self, event: Event):
        self.__eventBus.fireEvent(event)

    def _installEventHandler(self, eventType: type, handler):
        self.__eventBus.installEventHandler(
            eventType=eventType, handler=handler)

    def _installTimerHandler(
            self, frequency: float, handlers: list, oneShot: bool=False):
        return self.__eventBus.installTimerHandler(
            frequency=frequency, handlers=handlers, oneShot=oneShot)