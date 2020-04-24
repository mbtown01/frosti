from threading import Event as ThreadingEvent
from sys import maxsize
from time import time


class TimerBasedHandler:
    """ Invokes a handler based on a set number of ticks """
    ONE_SHOT_COMPLETED = -1

    def __init__(
            self,
            frequency: float,
            handlers: list,
            oneShot: bool,
            sync: ThreadingEvent):
        """ Creates a new TimerBasedHandler

        frequency: float
            Time in fractional seconds to wait between invocations
        handlers: list
            List of handlers, called in sequential/rotating order
        oneShot: bool
            True if this timer is intended on only firing once and not at a
            set frequency
        sync: ThreadingEvent
            Threading object, for internal use
        """
        self.__frequency = frequency
        self.__handlers = handlers
        if type(self.__handlers) is not list:
            self.__handlers = [handlers]
        self.__lastHandler = 0
        self.__lastInvoke = None
        self.__eventBusSync = sync
        self.__oneShot = oneShot

    def __repr__(self):
        return f"{self.__handlers[self.__lastHandler]}"

    @property
    def isQueued(self):
        """ True if this handler is active and will be run again"""
        if self.__oneShot:
            return self.__lastInvoke != self.ONE_SHOT_COMPLETED

        return True

    def getNextInvoke(self, now: float):
        """ Compute the next time this invoker should execute """
        self.__lastInvoke = self.__lastInvoke or now
        if self.ONE_SHOT_COMPLETED == self.__lastInvoke:
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

    def disable(self):
        self.__lastInvoke = self.ONE_SHOT_COMPLETED

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
