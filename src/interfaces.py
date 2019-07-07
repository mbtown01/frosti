from enum import Enum
from queue import Queue
from threading import Thread


class EventType(Enum):
    BUTTON_1 = 1
    BUTTON_2 = 2
    BUTTON_3 = 3
    BUTTON_4 = 4
    TEMPERATURE = 5
    PRESSURE = 6
    HUMIDITY = 7


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
    __staticInstance = None

    def __init__(self, eventBus: EventBus):
        self.__eventBus = eventBus
        self.__eventQueue = eventBus.subscribe()

        self.__eventHandlers = {}
        for eventType in EventType:
            self.__eventHandlers[eventType] = self.processUnhandled

    def processUnhandled(self, event: Event):
        pass

    def _processEvents(self):
        while self.__eventQueue.qsize():
            event = self.__eventQueue.get()
            self.__eventHandlers[event.getType()](event)

    def _putEvent(self, event: Event):
        self.__eventBus.put(event)

    def _subscribe(self, eventType: EventType, handler):
        self.__eventHandlers[eventType] = handler

    def exec(self):
        raise NotImplementedError()

    @classmethod
    def getInstance(cls):
        return cls.__staticInstance

    @classmethod
    def startEventHandler(cls, handler, threadName: str):
        cls.__staticInstance = handler
        handlerThread = Thread(
            target=handler.exec,
            name=threadName)
        handlerThread.daemon = True
        handlerThread.start()
