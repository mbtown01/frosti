import unittest
from queue import Queue

from src.events import EventBus, EventType, EventHandler, Event


class Test_EventBus(unittest.TestCase):

    def test_put(self):
        eventBus = EventBus()
        queue = eventBus.subscribe()
        event = Event(EventType.READING_TEMPERATURE)
        eventBus.put(event)

        self.assertEqual(1, queue.qsize())
        self.assertEqual(event.getType(), EventType.READING_TEMPERATURE)


class Test_EventHandler(unittest.TestCase):

    class DummyEventHandler(EventHandler):
        def __init__(self, eventBus: EventBus):
            super().__init__(eventBus)
            self.eventCount = 0

        def _processUnhandled(self, event: Event):
            self.eventCount += 1

    @classmethod
    def setup_class(cls):
        cls.eventBus = EventBus()
        cls.eventHandler = Test_EventHandler.DummyEventHandler(cls.eventBus)

        cls.eventBus.put(Event(EventType.READING_TEMPERATURE))
        cls.eventBus.put(Event(EventType.READING_PRESSURE))
        cls.eventBus.put(Event(EventType.READING_HUMIDITY))

    def test_processEvents(self):
        self.assertEqual(self.eventHandler.eventCount, 0)
        self.eventHandler.processEvents()
        self.assertEqual(self.eventHandler.eventCount, 3)

if __name__ == '__main__':
    unittest.main()
