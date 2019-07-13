from enum import Enum
from queue import Queue
from threading import Thread
from time import sleep


class Event:
    def __init__(self, data: dict={}):
        self._data = data.copy()

    def getData(self):
        return self._data.copy()


class FloatEvent(Event):
    def __init__(self, value: float):
        super().__init__({'value': value})

    def getValue(self):
        return float(self._data['value'])


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

    def __init__(self, eventBus: EventBus, loopSleep: float=1.0):
        self.__eventBus = eventBus
        self.__eventQueue = eventBus.subscribe()
        self.__loopSleep = loopSleep
        self.__eventHandlers = {}

    def processEvents(self):
        while self.__eventQueue.qsize():
            event = self.__eventQueue.get()
            if type(event) in self.__eventHandlers:
                self.__eventHandlers[type(event)](event)
            else:
                self._processUnhandled(event)

    def exec(self):
        while True:
            self.processEvents()
            sleep(self.__loopSleep)

    def _putEvent(self, event: Event):
        self.__eventBus.put(event)

    def _subscribe(self, eventType: type, handler):
        self.__eventHandlers[eventType] = handler

    def _processUnhandled(self, event: Event):
        pass

    @classmethod
    def startEventHandler(cls, handler, threadName: str):
        handlerThread = Thread(
            target=handler.exec,
            name=threadName)
        handlerThread.daemon = True
        handlerThread.start()
