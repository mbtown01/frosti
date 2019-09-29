import unittest
import sys

from src.events import Event, EventBus, EventHandler
from src.settings import Settings, SettingsChangedEvent

json = {
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
                "days": [0, 1, 2, 3, 4],
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
        self.eventBus = EventBus()
        self.settings = Settings(json=json)

    def test_initial(self):
        self.assertEqual(self.settings.comfortMin, 68.0)
