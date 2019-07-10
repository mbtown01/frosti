import unittest
from queue import Queue

from src.events import EventBus, Event, EventType, EventHandler, FloatEvent
from src.thermostat import ThermostatDriver


class Test_Thermostat(unittest.TestCase):

    class DummyEventHandler(EventHandler):
        def __init__(self, eventBus: EventBus):
            super().__init__(eventBus)
            self.eventCount = 0

        def _processUnhandled(self, event: Event):
            self.eventCount += 1

    @classmethod
    def setup_class(cls):
        cls.eventBus = EventBus()
        cls.dummyEventHandler = Test_Thermostat.DummyEventHandler(cls.eventBus)
        cls.thermostatDriver = ThermostatDriver(cls.eventBus)
        cls.thermostatDriver.processEvents()

    def test_simple(self):
        self.eventBus.put(Event(EventType.READING_TEMPERATURE, 68.0))
        self.eventBus.put(Event(EventType.READING_TEMPERATURE, 69.0))
        self.eventBus.put(Event(EventType.READING_TEMPERATURE, 70.0))
        self.eventBus.put(Event(EventType.READING_TEMPERATURE, 71.0))
        self.eventBus.put(Event(EventType.READING_TEMPERATURE, 72.0))


if __name__ == '__main__':
    unittest.main()
