import unittest
from queue import Queue
from time import sleep

from src.events import Event, EventBus, EventHandler
from src.thermostat import \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


class Test_EventBus(unittest.TestCase):

    def test_put(self):
        eventBus = EventBus()
        queue = eventBus.subscribe()
        event = TemperatureChangedEvent(0.0)
        eventBus.put(event)

        self.assertEqual(1, queue.qsize())
        self.assertEqual(type(event), TemperatureChangedEvent)


class Test_EventHandler(unittest.TestCase):

    class DummyEventHandler(EventHandler):
        def __init__(self, eventBus: EventBus):
            super().__init__(eventBus, 0.1)
            self.eventCount = 0

        def _processUnhandled(self, event: Event):
            self.eventCount += 1

    def test_simpleEvent(self):
        event = Event('test', {'foo': 'bar'})
        self.assertEqual('bar', event.data['foo'])
        self.assertEqual('test', repr(event))

    def test_processEvents(self):
        self.eventBus = EventBus()
        self.eventHandler = Test_EventHandler.DummyEventHandler(self.eventBus)
        self.eventBus.put(TemperatureChangedEvent(0.0))
        self.eventBus.put(PressureChangedEvent(0.0))
        self.eventBus.put(HumidityChangedEvent(0.0))

        self.assertEqual(self.eventHandler.eventCount, 0)
        self.eventHandler.processEvents()
        self.assertEqual(self.eventHandler.eventCount, 3)

    def test_processEventsThreaded(self):
        self.eventBus = EventBus()
        self.eventHandler = Test_EventHandler.DummyEventHandler(self.eventBus)
        self.eventHandler.start('Test Event Handler')

        self.assertEqual(self.eventHandler.eventCount, 0)
        self.eventBus.put(TemperatureChangedEvent(0.0))
        self.eventBus.put(PressureChangedEvent(0.0))
        self.eventBus.put(HumidityChangedEvent(0.0))

        # Thread is sleeping loopSleep seconds, need to be sure we
        # wait long enough for the events to have been processed
        sleep(2*self.eventHandler.loopSleep)
        self.eventHandler.stop()

        self.assertEqual(self.eventHandler.eventCount, 3)
