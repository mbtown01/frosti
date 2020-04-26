from threading import Event as ThreadingEvent
from sys import maxsize


class EventBusTimer:
    """ Invokes a handler based on a set number of ticks """
    ONE_SHOT_COMPLETED = -1

    def __init__(
            self,
            frequency: float,
            handler,
            oneShot: bool,
            sync: ThreadingEvent):
        """ Creates a new EventBusTimer

        frequency: float
            Time in fractional seconds to wait between invocations
        handler: method
            Method to be called when timer expires
        oneShot: bool
            True if this timer is intended on only firing once and not at a
            set frequency
        sync: ThreadingEvent
            Threading object, for internal use
        """
        self.__frequency = frequency
        self.__handler = handler
        self.__lastInvoke = None
        self.__eventBusSync = sync
        self.__oneShot = oneShot

    def __repr__(self):
        return f"{self.__handler}"

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
        self.__handler()
        self.__lastInvoke = now
        if self.__oneShot:
            self.__lastInvoke = self.ONE_SHOT_COMPLETED

    def disable(self):
        self.__lastInvoke = self.ONE_SHOT_COMPLETED

    def reset(self, handler: int=None, frequency: float=None):
        """ Resets this handler to a new state

        handler: int
            Integer offset in handler list to fire next, default is 0
        frequency: float
            New frequency for this timer, default is no change
         """
        self.__frequency = frequency or self.__frequency
        self.__lastInvoke = None
        self.__eventBusSync.set()
