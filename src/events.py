from queue import Queue
from threading import Event as ThreadingEvent
from sys import exc_info, maxsize
from time import time

from src.logging import log


class TimerBasedHandler:
    """ Invokes a handler based on a set number of ticks """
    ONE_SHOT_COMPLETED = -1

    def __init__(
            self,
            frequency: float,
            handlers: list,
            oneShot: bool,
            sync: ThreadingEvent):
        """ Creates a new CounterBasedInvoker

        frequency: float
            Time in fractional seconds to wait between invocations
        handlers: list
            List of handlers, called in sequential/rotating order
        """
        self.__frequency = frequency
        self.__handlers = handlers
        self.__lastHandler = 0
        self.__lastInvoke = None
        self.__eventBusSync = sync
        self.__oneShot = oneShot

    @property
    def isQueued(self):
        """ True if this handler is active and will be run again"""
        if self.__oneShot:
            return self.__lastInvoke != self.ONE_SHOT_COMPLETED

        return True

    @property
    def frequency(self):
        """ Time in fractional seconds to wait between invocations """
        return self.__frequency

    def getNextInvoke(self, now: float):
        """ Compute the next time this invoker should execute """
        self.__lastInvoke = self.__lastInvoke or now
        if self.__oneShot and self.ONE_SHOT_COMPLETED == self.__lastInvoke:
            return maxsize
        return self.__lastInvoke + self.__frequency

    def invoke(self, now: float):
        """ Invoke the current handler and mark the current time """
        self.invokeCurrent()
        self.__lastInvoke = now
        if self.__oneShot:
            self.__lastInvoke = self.ONE_SHOT_COMPLETED
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
        self.__lastInvoke = None
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
        """ Installs the provided handler method as a callback for when
        events of 'eventType' are fired on the event bus.

        eventType: type
            Type of event to listen for
        handler: method
            Method to register as a callback """
        if eventType not in self.__eventHandlers:
            self.__eventHandlers[eventType] = []
        self.__eventHandlers[eventType].append(handler)

    def installTimerHandler(
            self, frequency: float, handlers: list, oneShot: bool=False):
        """ Installs the provided list of handlers as a series of callbacks
        to be called at the provided frequency.  If more than one handler is
        provided, handlers are rotated through one at a time on successive
        invocations

        frequency: float
            Frequency at which to fire the series of handlers
        handlers: list
            List of handlers to rotate through
        oneShot: boolean
            If true, timer is only fired once and not again until it receives
            a call to reset() """
        handler = TimerBasedHandler(
            sync=self.__threadingEvent,
            frequency=frequency,
            handlers=handlers,
            oneShot=oneShot)
        self.__timerHandlers.append(handler)
        return handler

    def fireEvent(self, event: Event):
        """ Fires the event to any subscribed EventHandlers """
        self.__eventQueue.put(event)
        self.__threadingEvent.set()

    def processEvents(self, now: float=1):
        """ Process any events that have been generated since the last call,
        compute and return the time to wait until call method should be
        called again."""
        if now <= 0:
            raise RuntimeError(
                f"EventBus.processEvents:  now must be >0, received {now}")

        # Check if any timers need handling
        timeout = 60
        for handler in self.__timerHandlers:
            nextInvoke = handler.getNextInvoke(now)
            if nextInvoke < (now + 0.2):
                handler.invoke(now)
            else:
                timeout = min(timeout, nextInvoke-now)

        # Check events first, only delivering them to registered subscribers
        while self.__eventQueue.qsize():
            event = self.__eventQueue.get()
            if type(event) in self.__eventHandlers:
                for handler in self.__eventHandlers[type(event)]:
                    handler(event)

        return timeout

    def exec(self, iterations: int=maxsize):
        """ Drive the main application loop for some number of iterations,
        using the system time() command to tell processEvents the current
        time """
        iterationCount = 0

        while iterationCount < iterations:
            try:
                timeout = self.processEvents(now=time())

                iterationCount += 1
                if iterationCount < iterations:
                    log.debug(f"wait timout is {timeout}")
                    self.__threadingEvent.wait(timeout)
                    self.__threadingEvent.clear()
            except:
                log.warning(
                    "Invoker caught exception: " + exc_info())


class EventHandler:
    """ Simple helper base class that houses the EventBus """

    def __init__(self, eventBus: EventBus):
        self.__eventBus = eventBus

    def _fireEvent(self, event: Event):
        self.__eventBus.fireEvent(event)

    def _installEventHandler(self, eventType: type, handler):
        self.__eventBus.installEventHandler(
            eventType=eventType, handler=handler)

    def _installTimerHandler(
            self, frequency: float, handlers: list, oneShot: bool=False):
        return self.__eventBus.installTimerHandler(
            frequency=frequency, handlers=handlers, oneShot=oneShot)
