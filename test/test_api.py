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

programs:
    away:
        comfortMin: 64.0
        comfortMax: 78.0
        priceOverrides:
            - { price: 0.25, comfortMax: 82.0, comfortMin: null }
    overnight:
        comfortMin: 68.0
        comfortMax: 72.0
        priceOverrides:
            - { price: 0.25, comfortMax: 76.0, comfortMin: null }
            - { price: 0.50, comfortMax: 78.0, comfortMin: null }
            - { price: 1.00, comfortMax: 88.0, comfortMin: null }
    home:
        comfortMin: 70.0
        comfortMax: 76.0
        priceOverrides:
            - { price: 0.50, comfortMax: 80.0, comfortMin: null }
            - { price: 1.00, comfortMax: 88.0, comfortMin: null }
schedules:
    work week:
        days: [0, 1, 2, 3, 4]
        times:
            - { hour: 8, minute: 0, program: away }
            - { hour: 17, minute: 0, program: home }
            - { hour: 20, minute: 0, program: overnight }
    weekend:
        days: [5, 6]
        times:
            - { hour: 8, minute: 0, program: home }
            - { hour: 20, minute: 0, program: overnight }
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
        # cls.ormManagementService.importFromDict(
        #     yaml.load(yamlText, Loader=yaml.FullLoader))
        cls.serviceProvider.installService(
            OrmManagementService, cls.ormManagementService)

        configData = yaml.load(yamlText, Loader=yaml.FullLoader)
        cls.apiDataBroker = ApiDataBrokerService()
        cls.apiDataBroker.setServiceProvider(cls.serviceProvider)
        cls.apiDataBroker.setConfig(configData['config'])
        cls.apiDataBroker.setPrograms(configData['programs'])
        cls.apiDataBroker.setSchedules(configData['schedules'])

        cls.thermostat = ThermostatService()
        cls.thermostat.setServiceProvider(cls.serviceProvider)
        cls.serviceProvider.installService(
            ThermostatService, cls.thermostat)

        cls.__eventThread = Thread(
            target=cls.eventBus.exec,
            name='EventBus Driver')
        cls.__eventThread.daemon = True
        cls.__eventThread.start()

    def teardown_class(cls):
        apiKey = cls.apiDataBroker.sessionApiKey
        requests.post(API_URL + f'/api/v1/action/stop?key={apiKey}')

    def setup_method(self, method):
        def safelySetup(thermostat):
            thermostat.comfortMin = 68.0
            thermostat.comfortMax = 75.0
            thermostat.mode = ThermostatMode.COOL

        self.eventBus.fireEvent(SensorDataChangedEvent(
            temperature=72.5, pressure=1015.2, humidity=42.2))
        self.eventBus.safeInvoke(safelySetup, thermostat=self.thermostat)

    def test_temp_change1(self):
        req = requests.post(API_URL + '/api/v1/action/changeComfort?offset=2')
        data = req.json()
        self.assertTrue('comfortMax' in data)
        self.assertEqual(77.0, data['comfortMax'])

    def test_temp_change2(self):
        req = requests.post(API_URL + '/api/v1/action/changeComfort?offset=-2')
        data = req.json()
        self.assertTrue('comfortMax' in data)
        self.assertEqual(73.0, data['comfortMax'])

    def test_temp_change3(self):
        req = requests.post(API_URL + '/api/v1/action/changeComfort?value=80')
        data = req.json()
        self.assertTrue('comfortMax' in data)
        self.assertEqual(80.0, data['comfortMax'])

    def test_config_get_1(self):
        req = requests.get(API_URL + '/api/v1/config')
        data = req.json()
        expected = yaml.load(yamlText, Loader=yaml.FullLoader)['config']
        for key, value in data.items():
            self.assertEqual(str(expected[key]), str(value))

    def test_config_get_2(self):
        name = 'thermostat.delta'
        req = requests.get(API_URL + f'/api/v1/config/{name}')
        data = req.json()
        expected = yaml.load(yamlText, Loader=yaml.FullLoader)['config'][name]
        self.assertEqual(str(data), str(expected))

    def test_config_put_2(self):
        name = 'thermostat.delta'
        requests.put(API_URL + f'/api/v1/config/{name}', json='150')
        req = requests.get(API_URL + f'/api/v1/config/{name}')
        data = req.json()
        self.assertEqual('150', data)

    def test_config_put_3(self):
        jsonData = {
            'thermostat.delta': '123',
            'thermostat.fanRunoutDuration': '10130',
        }
        requests.put(API_URL + '/api/v1/config', json=jsonData)
        req = requests.get(API_URL + '/api/v1/config')
        data = req.json()
        self.assertEqual(data, jsonData)

    def test_config_patch(self):
        jsonData = {
            'thermostat.delta': '123',
            'thermostat.fanRunoutDuration': '10130',
        }
        requests.patch(API_URL + '/api/v1/config', json=jsonData)
        req = requests.get(API_URL + '/api/v1/config')
        data = req.json()
        expected = yaml.load(yamlText, Loader=yaml.FullLoader)['config']
        self.assertEqual(len(data), len(expected))
        for key, value in jsonData.items():
            self.assertEqual(data[key], jsonData[key])

    def test_programs_get_1(self):
        req = requests.get(API_URL + '/api/v1/programs')
        data = req.json()
        expected = yaml.load(yamlText, Loader=yaml.FullLoader)
        self.assertEqual(data, expected['programs'])

    def test_programs_get_2(self):
        req = requests.get(API_URL + '/api/v1/programs/doesnotexist')
        self.assertEqual(req.status_code, 404)

    def test_schedule_get_1(self):
        req = requests.get(API_URL + '/api/v1/schedules')
        data = req.json()
        expected = yaml.load(yamlText, Loader=yaml.FullLoader)
        self.assertEqual(data, expected['schedules'])

    def test_schedule_get_2(self):
        name = 'weekend'
        req = requests.get(API_URL + f'/api/v1/schedules/{name}')
        data = req.json()
        expected = yaml.load(yamlText, Loader=yaml.FullLoader)['schedules']
        self.assertEqual(data, expected[name])

    def test_schedule_put_1(self):
        name = 'weekend'
        jsonData = {
            'days': [5, 6],
            'times': [
                {'hour': 3, 'minute': 30, 'program': 'home'},
                {'hour': 9, 'minute': 30, 'program': 'overnight'},
                {'hour': 18, 'minute': 30, 'program': 'away'},
            ]
        }

        requests.put(API_URL + f'/api/v1/schedules/{name}', json=jsonData)
        req = requests.get(API_URL + '/api/v1/schedules')
        data = req.json()
        self.assertEqual(data[name], jsonData)
