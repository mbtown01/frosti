from queue import Queue
from threading import Event as ThreadingEvent
from sys import exc_info, maxsize
from time import time

from src.logging import log


class TimerBasedHandler:
    """ Invokes a handler based on a set number of ticks """

    def __init__(self, frequency: float, handlers: list, sync: ThreadingEvent):
        """ Creates a new CounterBasedInvoker

        frequency: float
            Time in fractional seconds to wait between invocations
        handlers: list
            List of handlers, called in sequential/rotating order
        """
        self.__frequency = frequency
        self.__handlers = handlers
        self.__lastHandler = 0
        self.__lastInvoke = time()
        self.__eventBusSync = sync

    @property
    def frequency(self):
        """ Time in fractional seconds to wait between invocations """
        return self.__frequency

    @property
    def lastInvoke(self):
        """ Time in fraction sections this handler was invoked """
        return self.__lastInvoke

    def invoke(self, now: float):
        """ Invoke the current handler and mark the current time """
        self.__lastInvoke = now
        self.invokeCurrent()
        self.__lastHandler = \
            (self.__lastHandler + 1) % len(self.__handlers)

    def invokeCurrent(self):
        """ Force an invoke of the current handler, does not update the
        lastInvoke timestamp """
        self.__handlers[self.__lastHandler]()

    def reset(self, handler: int=None, frequency: float=None):
        """ Resets this handler to a new state

        handler: int
            Integer offset in handler list to fire next, default is 0
        frequency: float
            New frequency for this timer, default is no change
         """
        self.__lastHandler = handler or 0
        self.__frequency = frequency or self.__frequency
        self.__lastInvoke = time()
        self.__eventBusSync.set()


class Event:
    def __init__(self, name: str=None, data: dict={}):
        self._data = data.copy()
        self.__name = name
        if name is None:
            name = type(self).__name__

    def __repr__(self):
        return self.__name

    @property
    def data(self):
        return self._data.copy()


class EventBus:
    """ Transceiver for all messaging, and owner of the main
    application thread """

    def __init__(self):
        self.__threadingEvent = ThreadingEvent()
        self.__timerHandlers = []
        self.__eventHandlers = {}
        self.__eventQueue = Queue()

    def installEventHandler(self, eventType: type, handler):
        if eventType not in self.__eventHandlers:
            self.__eventHandlers[eventType] = []
        self.__eventHandlers[eventType].append(handler)

    def installTimerHandler(self, frequency: float, handlers: list):
        handler = TimerBasedHandler(
            sync=self.__threadingEvent, frequency=frequency, handlers=handlers)
        self.__timerHandlers.append(handler)
        return handler

    def fireEvent(self, event: Event):
        """ Fires the event to all subscribed EventHandlers """
        self.__eventQueue.put(event)
        self.__threadingEvent.set()

    def processEvents(self, now: float=time()):
        """ Process any events that have been generated since the last call,
        compute and return the time to wait until call method should be
        called again """

        # For this tick, increment all invokers, potentially calling
        # processEvents and generating an exception
        while self.__eventQueue.qsize():
            event = self.__eventQueue.get()
            if type(event) in self.__eventHandlers:
                for handler in self.__eventHandlers[type(event)]:
                    try:
                        handler(event)
                    except:
                        log.warning(
                            "EventHandler caught exception: " + exc_info())

        timeout = 60
        for handler in self.__timerHandlers:
            nextInvoke = handler.lastInvoke + handler.frequency
            if nextInvoke <= now:
                timeout = min(timeout, handler.frequency)
                try:
                    handler.invoke(now)
                except:
                    log.warning(
                        "Invoker caught exception: " + exc_info())
            else:
                timeout = min(timeout, nextInvoke - now)

        return timeout

    def exec(self, iterations: int=maxsize):
        """ Drive the main application loop for some number of iterations """
        iterationCount = 0

        while iterationCount < iterations:
            timeout = self.processEvents(now=time())

            iterationCount += 1
            if iterationCount < iterations:
                self.__threadingEvent.wait(timeout)
                self.__threadingEvent.clear()


class EventHandler:
    """ Simple helper base class that houses the EventBus """

    def __init__(self, eventBus: EventBus):
        self.__eventBus = eventBus

    def _fireEvent(self, event: Event):
        self.__eventBus.fireEvent(event)

    def _installEventHandler(self, eventType: type, handler):
        self.__eventBus.installEventHandler(eventType, handler)

    def _installTimerHandler(self, frequency: float, handlers: list):
        return self.__eventBus.installTimerHandler(frequency, handlers)
