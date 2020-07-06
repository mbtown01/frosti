import unittest
from time import mktime, strptime

from src.core import EventBus, ServiceProvider
from src.core.events import PowerPriceChangedEvent
from src.services import ConfigService, OrmManagementService, ThermostatService

yamlData = """
thermostat:
    programs:
        away:
            comfortMin: 64
            comfortMax: 78
            priceOverrides:
                - { price: 0.25, comfortMax: 82 }
        overnight:
            comfortMin: 68
            comfortMax: 72
            priceOverrides:
                - { price: 0.25, comfortMax: 76 }
                - { price: 0.50, comfortMax: 78 }
                - { price: 1.00, comfortMax: 88 }
        home:
            comfortMin: 70
            comfortMax: 76
            priceOverrides:
                - { price: 0.50, comfortMax: 80 }
                - { price: 1.00, comfortMax: 88 }
    schedule:
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


class Test_Settings(unittest.TestCase):

    def setup_method(self, method):
        self.serviceProvider = ServiceProvider()
        self.eventBus = EventBus()
        self.serviceProvider.installService(EventBus, self.eventBus)
        self.config = ConfigService(yamlData=yamlData)
        self.serviceProvider.installService(ConfigService, self.config)
        self.ormManagementService = OrmManagementService(isTestInstance=True)
        self.ormManagementService.setServiceProvider(self.serviceProvider)
        self.ormManagementService.importFromYaml(yamlData)
        self.serviceProvider.installService(
            OrmManagementService, self.ormManagementService)
        self.thermostat = ThermostatService()
        self.thermostat.setServiceProvider(self.serviceProvider)
        self.serviceProvider.installService(
            ThermostatService, self.thermostat)

    def timeChanged(self, day: int, hour: int, minute: int):
        # This is a MONDAY
        testTime = strptime('12/31/18 00:00:01', '%m/%d/%y %H:%M:%S')
        time = mktime(testTime) + 60*(minute + 60*(hour + 24*day))
        self.eventBus.processEvents(time)
        time += 60*5
        self.eventBus.processEvents(time)

        return time

    def test_schedule1(self):
        """ Simple """
        self.timeChanged(0, 9, 0)
        self.assertEqual(self.thermostat.currentProgramName, 'away')
        self.assertEqual(self.thermostat.comfortMin, 64.0)
        self.assertEqual(self.thermostat.comfortMax, 78.0)

    def test_schedule2(self):
        """ Catch first part of the day, make sure last schedule applies """
        self.timeChanged(5, 0, 30)
        self.assertEqual(self.thermostat.currentProgramName, 'overnight')
        self.assertEqual(self.thermostat.comfortMin, 68.0)
        self.assertEqual(self.thermostat.comfortMax, 72.0)

    def test_schedule3(self):
        """ Catch a day not scheduled, make sure default applies """
        self.timeChanged(4, 0, 30)
        self.assertEqual(self.thermostat.currentProgramName, 'overnight')
        self.assertEqual(self.thermostat.comfortMin, 68.0)
        self.assertEqual(self.thermostat.comfortMax, 72.0)

    def test_schedule4(self):
        """ Catch the end of the day, make sure last entry applies """
        self.timeChanged(0, 21, 0)
        self.assertEqual(self.thermostat.currentProgramName, 'overnight')
        self.assertEqual(self.thermostat.comfortMin, 68.0)
        self.assertEqual(self.thermostat.comfortMax, 72.0)

    def test_user_change1(self):
        """ User override should last until next program """
        self.timeChanged(3, 0, 30)
        self.thermostat.comfortMax = 99.0
        self.thermostat.comfortMin = 55.0
        self.assertEqual(self.thermostat.comfortMin, 55.0)
        self.assertEqual(self.thermostat.comfortMax, 99.0)

        self.timeChanged(3, 10, 0)
        self.assertEqual(self.thermostat.currentProgramName, 'away')
        self.assertEqual(self.thermostat.comfortMin, 64.0)
        self.assertEqual(self.thermostat.comfortMax, 78.0)

    def test_price1(self):
        time = self.timeChanged(0, 4, 0)
        self.eventBus.fireEvent(PowerPriceChangedEvent(0.75, 300))
        self.eventBus.processEvents(time)
        self.assertEqual(self.thermostat.currentProgramName, 'overnight')
        self.assertTrue(self.thermostat.isInPriceOverride)
        self.assertEqual(self.thermostat.comfortMin, 68.0)
        self.assertEqual(self.thermostat.comfortMax, 78.0)

        self.eventBus.fireEvent(PowerPriceChangedEvent(0.05, 300))
        self.eventBus.processEvents(time+1200)
        self.assertEqual(self.thermostat.currentProgramName, 'overnight')
        self.assertFalse(self.thermostat.isInPriceOverride)
        self.assertEqual(self.thermostat.comfortMin, 68.0)
        self.assertEqual(self.thermostat.comfortMax, 72.0)

    def test_price_windowing(self):
        time = self.timeChanged(0, 9, 0)
        self.eventBus.fireEvent(PowerPriceChangedEvent(9.0, 300))
        self.eventBus.processEvents(time+300)
        self.assertTrue(self.thermostat.isInPriceOverride)
        self.assertEqual(self.thermostat.comfortMin, 68.0)
        self.assertEqual(self.thermostat.comfortMax, 82.0)

        self.eventBus.fireEvent(PowerPriceChangedEvent(0.05, 300))
        self.eventBus.processEvents(time+600)
        self.assertFalse(self.thermostat.isInPriceOverride)
        self.assertEqual(self.thermostat.currentProgramName, 'away')
        self.assertEqual(self.thermostat.comfortMin, 64.0)
        self.assertEqual(self.thermostat.comfortMax, 78.0)

        self.eventBus.fireEvent(PowerPriceChangedEvent(0.55, 300))
        self.eventBus.processEvents(time+1200)
        self.assertTrue(self.thermostat.isInPriceOverride)
        self.assertEqual(self.thermostat.comfortMin, 68.0)
        self.assertEqual(self.thermostat.comfortMax, 82.0)

        self.eventBus.fireEvent(PowerPriceChangedEvent(0.05, 300))
        self.eventBus.processEvents(time+2000)
        self.assertFalse(self.thermostat.isInPriceOverride)
        self.assertEqual(self.thermostat.currentProgramName, 'away')
        self.assertEqual(self.thermostat.comfortMin, 64.0)
        self.assertEqual(self.thermostat.comfortMax, 78.0)
