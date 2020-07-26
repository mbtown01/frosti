from queue import Queue
from threading import Event as ThreadingEvent
from sys import maxsize as MAX_INT
from time import time

from .EventBusTimer import EventBusTimer
from src.logging import log, handleException
from .Event import Event


class EventBus:
    """ Transceiver for all messaging, and owner of the main
    application thread """

    class __SafeInvokeEvent(Event):
        """ Encapsulates a method call as an event to be fired and handled
        by the EventBus event loop processing thread. """

        def __init__(self, method, *args, **kwargs):
            super().__init__('SafeInvokeEvent')
            self.__method = method
            self.__returnValue = None
            self.__exception = None
            self.__args = args
            self.__kwargs = kwargs
            self.__threadingEvent = ThreadingEvent()

        def execute(self):
            """ Calls the provided method on the appropriate thread, and then
            signals that the call was completed """
            try:
                self.__returnValue = \
                    self.__method(*self.__args, **self.__kwargs)
            except Exception as e:
                self.__exception = e
            finally:
                self.__threadingEvent.set()

        def wait(self, timeout=None):
            """ Waits for the execute() call to happen """
            self.__threadingEvent.wait(timeout)

            if self.__exception is not None:
                raise self.__exception

            return self.__returnValue

    def __init__(self, now: float = time()):
        self.__threadingEvent = ThreadingEvent()
        self.__timers = []
        self.__eventHandlers = {}
        self.__eventQueue = Queue()
        self.__now = now
        self.__stop = False

        self.installEventHandler(
            EventBus.__SafeInvokeEvent, self.__safeInvoke)

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

    def installTimer(
            self, frequency: float, handler, oneShot: bool = False):
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
        timer = EventBusTimer(
            sync=self.__threadingEvent,
            frequency=frequency,
            handler=handler,
            oneShot=oneShot)
        self.__timers.append(timer)
        return timer

    def fireEvent(self, event: Event, immediately: bool = False):
        """ Fires the event to any subscribed listeners

        immediately: bool
            True if the event should be dispatched on this call, otherwise
            the event is queued and processed at the next call to
            processEvents()
        """

        if immediately:
            eventHandlers = self.__eventHandlers.get(type(event), [])
            for handler in eventHandlers:
                handler(event)
        else:
            self.__eventQueue.put(event)
            self.__threadingEvent.set()

    def __safeInvoke(self, event: __SafeInvokeEvent):
        """ Executes the method but relies on the main loop for any exception
        handling """
        event.execute()

    def safeInvoke(self, methodCall, *args, **kwargs):
        """ Invoke the provided method call onto the event loop thread and
        provide the return value.

        This scenario is very important when events
        are coming in from another thread but need to interact safely with
        operations happening in the base event loop.  """
        event = EventBus.__SafeInvokeEvent(methodCall, *args, **kwargs)
        self.fireEvent(event)
        return event.wait()

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

    def processEvents(self, now: float = None):
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
        for timer in self.__timers:
            nextInvoke = timer.getNextInvoke(self.__now) - self.__now
            if nextInvoke < 0.2:
                try:
                    # log.debug(f"===> TIMER {timer}")
                    timer.invoke(self.__now)
                except:
                    handleException("processing timers")
            timeout = min(timeout, nextInvoke)

        # Only deliver events to registered subscribers
        while not self.__eventQueue.empty():
            event = self.__eventQueue.get()
            eventHandlers = self.__eventHandlers.get(type(event), [])
            for handler in eventHandlers:
                try:
                    # log.debug(f"===> HANDLER {handler}")
                    handler(event)
                except:
                    handleException("processing event queue")

        return max(0.0, timeout)

    def exec(self, iterations: int = MAX_INT):
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
                handleException("executing main event loop")
