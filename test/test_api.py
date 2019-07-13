import unittest
import requests
import sys
from time import sleep

from src.api import ApiEventHandler
from src.events import Event, EventBus, EventHandler
from src.thermostat import \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


class Test_ApiEventHandler(unittest.TestCase):

    def setup_method(self, method):
        self.eventBus = EventBus()
        self.apiEventHandler = ApiEventHandler(self.eventBus)
        sleep(0.1)

        self.testValueTemperature = 72.5
        self.testValuePressure = 1015.2
        self.testValueHumidity = 42.4
        self.eventBus.put(TemperatureChangedEvent(self.testValueTemperature))
        self.eventBus.put(PressureChangedEvent(self.testValuePressure))
        self.eventBus.put(HumidityChangedEvent(self.testValueHumidity))
        self.apiEventHandler.processEvents()

    def test_version(self):
        req = requests.get('http://localhost:5000/api/version')
        self.assertEqual(req.text, "rpt-0.1")

    def test_temperature(self):
        req = requests.get('http://localhost:5000/api/sensors/temperature')
        self.assertEqual(req.text, f"{self.testValueTemperature}")

    def test_pressure(self):
        req = requests.get('http://localhost:5000/api/sensors/pressure')
        self.assertEqual(req.text, f"{self.testValuePressure}")

    def test_humidity(self):
        req = requests.get('http://localhost:5000/api/sensors/humidity')
        self.assertEqual(req.text, f"{self.testValueHumidity}")
