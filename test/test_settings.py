import unittest
import sys
from time import mktime, strptime

from src.core import Event, EventBus, EventBusMember
from src.services import SettingsService
from src.core import ServiceProvider
from src.services import ConfigService

data = {
    "thermostat": {
        "delta": 1.0,
        "programs": {
            "_default": {
                "comfortMin": 68,
                "comfortMax": 75
            },
            "overnight": {
                "comfortMin": 68,
                "comfortMax": 72,
                "priceOverrides": [
                    {
                        "price": 0.25,
                        "comfortMax": 76
                    },
                    {
                        "price": 0.50,
                        "comfortMax": 78
                    },
                    {
                        "price": 1.00,
                        "comfortMax": 88
                    }
                ]
            },
            "home": {
                "comfortMin": 70,
                "comfortMax": 76,
                "priceOverrides": [
                    {
                        "price": 0.50,
                        "comfortMax": 80
                    },
                    {
                        "price": 1.00,
                        "comfortMax": 88
                    }
                ]
            },
            "away": {
                "comfortMin": 64,
                "comfortMax": 78,
                "priceOverrides": [
                    {
                        "price": 0.25,
                        "comfortMax": 82
                    }
                ]
            }
        },
        "schedule": {
            "work week": {
                "days": [0, 1, 2, 3],
                "times": [
                    {
                        "hour": 8,
                        "minute": 0,
                        "program": "away"
                    },
                    {
                        "hour": 17,
                        "minute": 0,
                        "program": "home"
                    },
                    {
                        "hour": 20,
                        "minute": 0,
                        "program": "overnight"
                    }
                ]
            },
            "weekend": {
                "days": [5, 6],
                "times": [
                    {
                        "hour": 8,
                        "minute": 0,
                        "program": "home"
                    },
                    {
                        "hour": 20,
                        "minute": 0,
                        "program": "overnight"
                    }
                ]
            }
        }
    }
}


class Test_Settings(unittest.TestCase):

    def setup_method(self, method):
        self.serviceProvider = ServiceProvider()
        testTime = strptime('01/01/19 08:01:00', '%m/%d/%y %H:%M:%S')
        self.eventBus = EventBus(now=mktime(testTime))
        self.serviceProvider.installService(EventBus, self.eventBus)
        self.config = ConfigService(data=data)
        self.serviceProvider.installService(ConfigService, self.config)
        self.settings = SettingsService()
        self.settings.setServiceProvider(self.serviceProvider)
        self.serviceProvider.installService(SettingsService, self.settings)

    def test_initial(self):
        self.assertEqual(self.settings.comfortMin, 68.0)
        self.assertEqual(self.settings.comfortMax, 75.0)

    def test_schedule1(self):
        """ Simple """
        self.settings.timeChanged(0, 9, 0)
        self.assertEqual(self.settings.comfortMin, 64.0)
        self.assertEqual(self.settings.comfortMax, 78.0)

    def test_schedule2(self):
        """ Catch first part of the day, make sure last schedule applies """
        self.settings.timeChanged(5, 0, 30)
        self.assertEqual(self.settings.comfortMin, 68.0)
        self.assertEqual(self.settings.comfortMax, 72.0)

    def test_schedule3(self):
        """ Catch a day not scheduled, make sure default applies """
        self.settings.timeChanged(4, 0, 30)
        self.assertEqual(self.settings.comfortMin, 68.0)
        self.assertEqual(self.settings.comfortMax, 75.0)

    def test_user_change1(self):
        """ User override should last until next program """
        self.settings.timeChanged(3, 0, 30)
        self.settings.comfortMax = 99.0
        self.settings.comfortMin = 55.0
        self.assertEqual(self.settings.comfortMin, 55.0)
        self.assertEqual(self.settings.comfortMax, 99.0)

        self.settings.timeChanged(3, 10, 0)
        self.assertEqual(self.settings.comfortMin, 64.0)
        self.assertEqual(self.settings.comfortMax, 78.0)

    def test_price1(self):
        self.settings.timeChanged(0, 9, 0)
        self.settings.priceChanged(2.0)
        self.assertEqual(self.settings.comfortMin, 64.0)
        self.assertEqual(self.settings.comfortMax, 82.0)

        self.settings.priceChanged(0.05)
        self.assertEqual(self.settings.comfortMin, 64.0)
        self.assertEqual(self.settings.comfortMax, 78.0)

    def test_price3(self):
        self.settings.timeChanged(4, 0, 30)
        self.settings.priceChanged(0)
        self.assertEqual(self.settings.comfortMin, 68.0)
        self.assertEqual(self.settings.comfortMax, 75.0)

        self.settings.priceChanged(0.05)
        self.assertEqual(self.settings.comfortMin, 68.0)
        self.assertEqual(self.settings.comfortMax, 75.0)

    def test_bad1(self):
        data = {
            "thermostat": {
                "delta": 1.0,
                "programs": {
                    "_default": {
                        "comfortMin": 68,
                        "comfortMax": 75
                    },
                    "overnight": {
                        "comfortMin": 68,
                        "comfortMax": 72
                    },
                },
                "schedule": {
                    "work week": {
                        "days": [0, 1, 2, 3],
                        "times": [
                            {
                                "hour": 8,
                                "minute": 0,
                                "program": "overnight"
                            },
                            {
                                "hour": 17,
                                "minute": 0,
                                "program": "bad_program"
                            }
                        ]
                    }
                }
            }
        }

        self.settings.__init__(data)
        with self.assertRaises(RuntimeError):
            self.settings.setServiceProvider(self.serviceProvider)
