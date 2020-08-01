import unittest
import requests
import yaml
from time import strptime, mktime
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

    def setup_class(cls):
        # This is a Tuesday FYI, day '1' of 7 [0-6], built manually in UTC
        # time to represent 8:01 AM in the America/Chicago time zone
        testTime = strptime('01/01/19 14:01:00', '%m/%d/%y %H:%M:%S')
        cls.serviceProvider = ServiceProvider()
        cls.eventBus = EventBus(now=mktime(testTime))
        cls.serviceProvider.installService(EventBus, cls.eventBus)
        cls.ormManagementService = OrmManagementService(isTestInstance=True)
        cls.ormManagementService.setServiceProvider(cls.serviceProvider)
        cls.ormManagementService.importFromDict(
            yaml.load(yamlText, Loader=yaml.FullLoader))
        cls.serviceProvider.installService(
            OrmManagementService, cls.ormManagementService)
        cls.thermostat = ThermostatService()
        cls.thermostat.setServiceProvider(cls.serviceProvider)
        cls.serviceProvider.installService(
            ThermostatService, cls.thermostat)

        cls.apiDataBroker = ApiDataBrokerService()
        cls.apiDataBroker.setServiceProvider(cls.serviceProvider)

        cls.__eventThread = Thread(
            target=cls.eventBus.exec,
            name='EventBus Driver')
        cls.__eventThread.daemon = True
        cls.__eventThread.start()

    def teardown_class(cls):
        apiKey = cls.apiDataBroker.sessionApiKey
        requests.post(API_URL + f'/api/action/stop?key={apiKey}')

    def setup_method(self, method):
        def safelySetup(thermostat):
            thermostat.comfortMin = 68.0
            thermostat.comfortMax = 75.0
            thermostat.mode = ThermostatMode.COOL

        self.eventBus.fireEvent(SensorDataChangedEvent(
            temperature=72.5, pressure=1015.2, humidity=42.2))
        self.eventBus.safeInvoke(safelySetup, thermostat=self.thermostat)

    def test_status(self):
        req = requests.get(API_URL + '/api/status')
        data = req.json()
        self.assertTrue('version' in data)

    def test_temp_change1(self):
        req = requests.post(API_URL + '/api/action/raiseComfort?offset=2')
        data = req.json()
        self.assertTrue('comfortMax' in data)
        self.assertEqual(77.0, data['comfortMax'])

    def test_temp_change2(self):
        req = requests.post(API_URL + '/api/action/lowerComfort?offset=2')
        data = req.json()
        self.assertTrue('comfortMax' in data)
        self.assertEqual(73.0, data['comfortMax'])

    def test_temp_change3(self):
        req = requests.post(API_URL + '/api/action/changeComfort?value=80')
        data = req.json()
        self.assertTrue('comfortMax' in data)
        self.assertEqual(80.0, data['comfortMax'])
