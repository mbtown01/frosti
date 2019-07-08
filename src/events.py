from enum import Enum
from queue import Queue
from threading import Thread
from time import sleep


class EventType(Enum):
    IGNORE = 0x00
    SETTINGS_CHANGED = 0x01
    READING_TEMPERATURE = 0x10
    READING_PRESSURE = 0x11
    READING_HUMIDITY = 0x12


class Event:
    def __init__(self, type: EventType, data: dict={}):
        self.__type = type
        self.__data = data

    def getType(self):
        return self.__type

    def getData(self):
        return self.__data.copy()


class FloatEvent(Event):
    def __init__(self, type: EventType, value: float):
        self.__value = value
        super().__init__(type, {'value': value})

    def getValue(self):
        return self.__value


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
        for eventType in EventType:
            self.__eventHandlers[eventType] = self.__processUnhandled

    def processEvents(self):
        while self.__eventQueue.qsize():
            event = self.__eventQueue.get()
            self.__eventHandlers[event.getType()](event)

    def exec(self):
        while True:
            self.processEvents()
            sleep(self.__loopSleep)

    def _putEvent(self, event: Event):
        self.__eventBus.put(event)

    def _subscribe(self, eventType: EventType, handler):
        self.__eventHandlers[eventType] = handler

    def __processUnhandled(self, event: Event):
        pass

    @classmethod
    def startEventHandler(cls, handler, threadName: str):
        handlerThread = Thread(
            target=handler.exec,
            name=threadName)
        handlerThread.daemon = True
        handlerThread.start()
