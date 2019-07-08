import unittest
from queue import Queue

from src.events import EventBus, EventType, EventHandler, FloatEvent
from src.thermostat import ThermostatDriver


class Test_Thermostat(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        cls.eventBus = EventBus()
        cls.thermostatDriver = ThermostatDriver(cls.eventBus)
        EventHandler.startEventHandler(
            cls.thermostatDriver, 'API Event Driver')

        cls.testValueTemperature = 72.5
        cls.testValuePressure = 1015.2
        cls.testValueHumidity = 42.4
        cls.eventBus.put(
            FloatEvent(
                EventType.READING_TEMPERATURE, cls.testValueTemperature))
        cls.eventBus.put(
            FloatEvent(EventType.READING_PRESSURE, cls.testValuePressure))
        cls.eventBus.put(
            FloatEvent(EventType.READING_HUMIDITY, cls.testValueHumidity))
        cls.thermostatDriver.processEvents()

    def test_put(self):
        pass


if __name__ == '__main__':
    unittest.main()
