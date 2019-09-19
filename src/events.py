from queue import Queue
from threading import Thread
from time import sleep


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
    def __init__(self):
        self.__queueList = []

    def subscribe(self):
        queue = Queue()
        self.__queueList.append(queue)
        return queue

    def put(self, event: Event):
        for queue in self.__queueList:
            queue.put(event)


class EventHandler:
    """ Sits on the event bus and can either consume or produce events. """

    def __init__(self, eventBus: EventBus, loopSleep: float=1.0):
        self.__eventBus = eventBus
        self.__eventQueue = eventBus.subscribe()
        self.__loopSleep = loopSleep
        self.__shouldStop = False
        self.__eventHandlers = {}

    @property
    def loopSleep(self):
        """ How much time to sleep between processing events, in
        fractional seconds """
        return self.__loopSleep

    def processEvents(self):
        """ Processes all events currently in this handler's queue """
        while self.__eventQueue.qsize():
            event = self.__eventQueue.get()
            if type(event) in self.__eventHandlers:
                self.__eventHandlers[type(event)](event)
            else:
                self._processUnhandled(event)

    def start(self, threadName: str):
        """ Runs exec() on another thread and then returns """
        self.__thread = Thread(target=self.exec, name=threadName)
        self.__thread.daemon = True
        self.__thread.start()

    def join(self):
        if self.__thread is None:
            raise RuntimeError("Attempt to join an unthreaded EventHandler")
        self.__thread.join()

    def stop(self):
        """ Stops the exec() loop at the next iteration """
        self.__shouldStop = True

    def exec(self):
        """ Calls processEvents() and then sleeps for self.loopSleep
        seconds until stop() is called """
        while not self.__shouldStop:
            self.processEvents()
            sleep(self.loopSleep)

    def _fireEvent(self, event: Event):
        """ Places an event on the event queue for all other event
        handlers to see """
        self.__eventBus.put(event)

    def _subscribe(self, eventType: type, handler):
        """ Subscribes a handler to a specific type of event, which is
        called during processEvents() should that event appear on the
        EventBus """
        self.__eventHandlers[eventType] = handler

    def _processUnhandled(self, event: Event):
        """ Default method called for an event that this handler has
        not subscribed to.  Designed to be overridden in derived classes,
        is a 'pass' by default """
        pass
