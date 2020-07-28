import unittest
import requests
import json
import yaml
from time import sleep, strptime, mktime
from threading import Thread

from src.services import ApiDataBrokerService
from src.core import EventBus, ServiceProvider, ThermostatMode
from src.services import ThermostatService, OrmManagementService
from src.core.events import SensorDataChangedEvent

yamlText = """
config:
    thermostat.delta: 1.0
    thermostat.fanRunoutDuration: 30
    thermostat.timezone: "America/Chicago"
    ui.backlightTimeout: 10
"""

API_URL = 'http://localhost:5000'


class Test_ApiDataBroker(unittest.TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)

        # This is a Tuesday FYI, day '1' of 7 [0-6], built manually in UTC
        # time to represent 8:01 AM in the America/Chicago time zone
        testTime = strptime('01/01/19 14:01:00', '%m/%d/%y %H:%M:%S')
        self.serviceProvider = ServiceProvider()
        self.eventBus = EventBus(now=mktime(testTime))
        self.serviceProvider.installService(EventBus, self.eventBus)
        self.ormManagementService = OrmManagementService(isTestInstance=True)
        self.ormManagementService.setServiceProvider(self.serviceProvider)
        self.ormManagementService.importFromDict(
            yaml.load(yamlText, Loader=yaml.FullLoader))
        self.serviceProvider.installService(
            OrmManagementService, self.ormManagementService)
        self.thermostat = ThermostatService()
        self.thermostat.setServiceProvider(self.serviceProvider)
        self.serviceProvider.installService(
            ThermostatService, self.thermostat)

        self.apiDataBroker = ApiDataBrokerService()
        self.apiDataBroker.setServiceProvider(self.serviceProvider)

        self.__eventThread = Thread(
            target=self.eventBus.exec,
            name='EventBus Driver')
        self.__eventThread.daemon = True
        self.__eventThread.start()

    def setup_method(self, method):
        self.thermostat.comfortMin = 68.0
        self.thermostat.comfortMax = 75.0
        self.thermostat.mode = ThermostatMode.COOL

        self.eventBus.fireEvent(SensorDataChangedEvent(
            temperature=72.5,
            pressure=1015.2,
            humidity=42.2))

    def test_status(self):
        req = requests.get(API_URL + '/api/status')
        data = json.loads(req.text)
        self.assertTrue('version' in data)

    def test_temp_change(self):
        req = requests.post(API_URL + '/api/action/raiseComfort?offset=2')
        data = json.loads(req.text)
        self.assertTrue('version' in data)
        self.assertTrue('comfortMax' in data)
        self.assertEqual(77.0, data['comfortMax'])
