from queue import Queue
from threading import Event as ThreadingEvent
from sys import exc_info, maxsize
from time import time

from .TimerBasedHandler import TimerBasedHandler
from src.logging import log
from .Event import Event


class EventBus:
    """ Transceiver for all messaging, and owner of the main
    application thread """

    def __init__(self, now: float=time()):
        self.__threadingEvent = ThreadingEvent()
        self.__timerHandlers = []
        self.__eventHandlers = {}
        self.__eventQueue = Queue()
        self.__now = now
        self.__stop = False

    def installEventHandler(self, eventType: type, handler):
        """ Installs the provided handler method as a callback for when
        events of 'eventType' are fired on the event bus.

        eventType: typez
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
        """ Fires the event to any subscribed listeners """
        self.__eventQueue.put(event)
        self.__threadingEvent.set()

    @property
    def now(self):
        """ Gets the time of the last call to processEvents, or None.  This
        makes testing more straight forward because it enables an absolute
        time to be applied and not whatever time the test is running """
        return self.__now

    def stop(self):
        """ Stop all event processing, effectively initiating shutdown """
        self.__stop = True
        self.__threadingEvent.set()

    def processEvents(self, now: float=None):
        """ Process any events that have been generated since the last call,
        compute and return the time to wait until call method should be
        called again."""

        self.__now = now or self.__now
        if self.__now <= 0:
            raise RuntimeError(
                f"EventBus.processEvents:  now must be >0, got {self.__now}")

        # log.debug(f"EventBus::processEvents(now={now})")
        # Check if any timers need handling
        timeout = 60.0
        for handler in self.__timerHandlers:
            nextInvoke = handler.getNextInvoke(self.__now) - self.__now
            if nextInvoke < 0.2:
                try:
                    # log.debug(f"===> TIMER {handler}")
                    handler.invoke(self.__now)
                except:
                    log.error(
                        f"Handler encountered exception: {exc_info()}")
            timeout = min(timeout, nextInvoke)

        # Check events first, only delivering them to registered subscribers
        while not self.__eventQueue.empty():
            event = self.__eventQueue.get()
            eventHandlers = self.__eventHandlers.get(type(event), [])
            for handler in eventHandlers:
                try:
                    # log.debug(f"===> HANDLER {handler}")
                    handler(event)
                except:
                    log.error(
                        f"Handler encountered exception: {exc_info()}")

        return max(0.0, timeout)

    def exec(self, iterations: int=maxsize):
        """ Drive the main application loop for some number of iterations,
        using the system time() command to tell processEvents the current
        time """
        iterationCount = 0

        while not self.__stop and iterationCount < iterations:
            try:
                timeout = self.processEvents(time())

                iterationCount += 1
                if iterationCount < iterations:
                    if not self.__threadingEvent.is_set():
                        self.__threadingEvent.wait(timeout)
                    else:
                        self.__threadingEvent.clear()
            except KeyboardInterrupt:
                log.info("Keyboard interrupt received, shutting down")
                break
            except:
                info = exc_info()
                log.warning(f"Invoker caught exception: {info}")
