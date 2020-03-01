import unittest
import requests
import sys
import json
from time import sleep, strptime, mktime

from src.api import ApiDataBroker
from src.events import Event, EventBus
from src.services import ServiceProvider
from src.config import Config
from src.settings import Settings
from src.generics import SensorDataChangedEvent


class Test_ApiDataBroker(unittest.TestCase):

    def setup_method(self, method):
        self.serviceProvider = ServiceProvider()
        testTime = strptime('01/01/19 08:01:00', '%m/%d/%y %H:%M:%S')
        self.eventBus = EventBus(now=mktime(testTime))
        self.serviceProvider.installService(EventBus, self.eventBus)
        self.config = Config()
        self.serviceProvider.installService(Config, self.config)
        self.settings = Settings()
        self.settings.setServiceProvider(self.serviceProvider)
        self.serviceProvider.installService(Settings, self.settings)

        apiDataBroker = ApiDataBroker()
        apiDataBroker.setServiceProvider(self.serviceProvider)
        sleep(0.1)

        self.testValueTemperature = 72.5
        self.testValuePressure = 1015.2
        self.testValueHumidity = 42.4
        self.eventBus.fireEvent(SensorDataChangedEvent(
            temperature=self.testValueTemperature,
            pressure=self.testValuePressure,
            humidity=self.testValueHumidity))
        self.eventBus.processEvents()

    def test_status(self):
        req = requests.get('http://localhost:5000/api/status')
        data = json.loads(req.text)
        self.assertTrue('version' in data)

    def test_settings(self):
        req = requests.get('http://localhost:5000/api/settings')
        data = json.loads(req.text)
        self.assertTrue('version' in data)
