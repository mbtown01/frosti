import unittest
import requests
import sys
from time import sleep

from src.api import ApiEventHandler
from src.events import Event, EventBus, EventHandler
from src.thermostat import \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


class Test_ApiEventHandler(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        cls.eventBus = EventBus()
        cls.apiEventHandler = ApiEventHandler(cls.eventBus)
        sleep(0.1)

        cls.testValueTemperature = 72.5
        cls.testValuePressure = 1015.2
        cls.testValueHumidity = 42.4
        cls.eventBus.put(TemperatureChangedEvent(cls.testValueTemperature))
        cls.eventBus.put(PressureChangedEvent(cls.testValuePressure))
        cls.eventBus.put(HumidityChangedEvent(cls.testValueHumidity))
        cls.apiEventHandler.processEvents()

    def test_temperature(self):
        req = requests.get('http://localhost:5000/api/sensors/temperature')
        self.assertEqual(req.text, f"{self.testValueTemperature}")

    def test_pressure(self):
        req = requests.get('http://localhost:5000/api/sensors/pressure')
        self.assertEqual(req.text, f"{self.testValuePressure}")

    def test_humidity(self):
        req = requests.get('http://localhost:5000/api/sensors/humidity')
        self.assertEqual(req.text, f"{self.testValueHumidity}")


if __name__ == '__main__':
    unittest.main()
