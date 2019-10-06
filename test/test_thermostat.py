import unittest
import time

from src.events import EventBus, EventHandler
from src.settings import settings, Settings
from src.generics import ThermostatStateChangedEvent, ThermostatState, \
    GenericThermostatDriver, GenericLcdDisplay, GenericEnvironmentSensor, \
    GenericRelay


json = {
    "thermostat": {
        "delta": 1.0,
        "fanRunout": 30,
        "programs": {
            "_default": {
                "comfortMin": 32,
                "comfortMax": 212
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
                "comfortMin": 68,
                "comfortMax": 75,
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
                        "program": "away"
                    }
                ]
            }
        }
    }
}


# TODO: Defaults and current time/price configuration are different,
# check that startup sequence doesn't short-cycle the AC/HEAT

class Test_Thermostat(unittest.TestCase):

    class DummyEventHandler(EventHandler):
        def __init__(self, eventBus: EventBus):
            super().__init__(eventBus)
            super()._installEventHandler(
                ThermostatStateChangedEvent, self._thermostatStateChanged)

            self.__lastState = None

        @property
        def lastState(self):
            return self.__lastState

        def _thermostatStateChanged(self, event: ThermostatStateChangedEvent):
            self.__lastState = event.state

    class TestThermostatDriver(GenericThermostatDriver):

        def __init__(self,
                     sensor: GenericEnvironmentSensor,
                     relays: list,
                     eventBus: EventBus):
            # This is a Tuesday FYI, day '1' of 7 [0-6]
            # All tests should be in the 'away' program above
            self.localtime = time.strptime(
                '01/01/19 08:01:00', '%m/%d/%y %H:%M:%S')

            super().__init__(
                eventBus=eventBus,
                lcd=GenericLcdDisplay(20, 4),
                sensor=sensor,
                relays=relays
            )

        def _getLocalTime(self):
            """ Override local time for testing on a specific day relative
            to the json config being used for testing """
            return self.localtime

    def setup_method(self, method):
        self.eventBus = EventBus()
        self.now = 1.0
        settings.__init__(json)
        settings.mode = Settings.Mode.COOL
        settings.setEventBus(self.eventBus)

        self.dummyEventHandler = \
            Test_Thermostat.DummyEventHandler(self.eventBus)
        self.dummySensor = GenericEnvironmentSensor()
        self.relayList = (
            GenericRelay(ThermostatState.HEATING),
            GenericRelay(ThermostatState.COOLING),
            GenericRelay(ThermostatState.FAN),
        )
        self.relayMap = {r.function: r for r in self.relayList}
        self.thermostatDriver = Test_Thermostat.TestThermostatDriver(
            sensor=self.dummySensor,
            relays=self.relayList,
            eventBus=self.eventBus
        )
        self.eventBus.processEvents()

    def assertNextTemperature(
            self, temp: float, duration: float, state: ThermostatState):
        self.dummySensor.temperature = temp
        self.now += duration
        self.eventBus.processEvents(self.now)
        self.assertEqual(self.thermostatDriver.state, state)
        if state in self.relayMap:
            self.assertFalse(
                self.relayMap[state].isOpen,
                f"Relay {state} should be closed for state {state}")
            if state.shouldRunFan:
                self.assertFalse(
                    self.relayMap[ThermostatState.FAN].isOpen,
                    f"Relay FAN should be closed for state {state}")
        if state == ThermostatState.FAN_RUNOUT:
            self.assertFalse(
                self.relayMap[ThermostatState.FAN].isOpen,
                "Fan relay should be closed for state FAN_RUNOUT")

    def test_stateChangedCooling(self):
        settings.mode = Settings.Mode.COOL

        self.assertIsNone(self.dummyEventHandler.lastState)
        self.assertNextTemperature(78.0, 15, ThermostatState.COOLING)
        self.eventBus.processEvents()
        self.assertIsNotNone(self.dummyEventHandler.lastState)
        self.assertEqual(
            self.dummyEventHandler.lastState, ThermostatState.COOLING)

    def test_stateChangedHeating(self):
        settings.mode = Settings.Mode.HEAT

        self.assertIsNone(self.dummyEventHandler.lastState)
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)
        self.eventBus.processEvents()
        self.assertIsNotNone(self.dummyEventHandler.lastState)
        self.assertEqual(
            self.dummyEventHandler.lastState, ThermostatState.HEATING)

    def test_stateChangedHeatToOff(self):
        settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        settings.mode = Settings.Mode.OFF
        self.assertNextTemperature(60.0, 15, ThermostatState.OFF)

    def test_stateChangedHeatToCool(self):
        settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        settings.mode = Settings.Mode.COOL
        self.assertNextTemperature(60.0, 15, ThermostatState.OFF)

    def test_stateChangedCoolToHeat(self):
        settings.mode = Settings.Mode.COOL
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(80.0, 15, ThermostatState.OFF)

    def test_simpleCool(self):
        settings.mode = Settings.Mode.COOL

        self.assertNextTemperature(75.0, 15, ThermostatState.OFF)
        self.assertNextTemperature(78.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, 15, ThermostatState.FAN_RUNOUT)
        self.assertNextTemperature(73.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(73.0, 1000, ThermostatState.OFF)

    def test_simpleHeat(self):
        settings.mode = Settings.Mode.HEAT

        self.assertNextTemperature(68.0, 15, ThermostatState.OFF)
        self.assertNextTemperature(65.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(68.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(70.0, 15, ThermostatState.FAN_RUNOUT)
        self.assertNextTemperature(70.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(70.0, 1000, ThermostatState.OFF)

    def test_simpleAuto(self):
        settings.mode = Settings.Mode.AUTO

        self.assertNextTemperature(75.0, 15, ThermostatState.OFF)
        self.assertNextTemperature(78.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, 15, ThermostatState.FAN_RUNOUT)
        self.assertNextTemperature(73.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(68.0, 1000, ThermostatState.OFF)
        self.assertNextTemperature(65.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(68.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(70.0, 15, ThermostatState.FAN_RUNOUT)
        self.assertNextTemperature(70.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(70.0, 1000, ThermostatState.OFF)
