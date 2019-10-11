import unittest
from time import mktime, strptime

from src.events import EventBus, EventHandler
from src.services import ServiceProvider
from src.settings import Settings
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
        def __init__(self):
            self.__lastState = None

        def setServiceProvider(self, provider: ServiceProvider):
            super().setServiceProvider(provider)
            super()._installEventHandler(
                ThermostatStateChangedEvent, self._thermostatStateChanged)

        @property
        def lastState(self):
            return self.__lastState

        def _thermostatStateChanged(self, event: ThermostatStateChangedEvent):
            self.__lastState = event.state

    class TestThermostatDriver(GenericThermostatDriver):

        def __init__(self,
                     localtime: float,
                     sensor: GenericEnvironmentSensor,
                     relays: list):
            # This is a Tuesday FYI, day '1' of 7 [0-6]
            # All tests should be in the 'away' program above
            self.localtime = localtime

            super().__init__(
                lcd=GenericLcdDisplay(20, 4),
                sensor=sensor,
                relays=relays
            )

        def _getLocalTime(self):
            """ Override local time for testing on a specific day relative
            to the json config being used for testing """
            return self.localtime

    def setup_method(self, method):
        self.serviceProvider = ServiceProvider()
        self.eventBus = EventBus()

        self.serviceProvider.installService(EventBus, self.eventBus)
        self.localtime = strptime(
            '01/01/19 08:01:00', '%m/%d/%y %H:%M:%S')
        self.now = mktime(self.localtime)
        self.settings = Settings(json)
        self.settings.setServiceProvider(self.serviceProvider)
        self.settings.mode = Settings.Mode.COOL
        self.serviceProvider.installService(Settings, self.settings)

        self.dummyEventHandler = \
            Test_Thermostat.DummyEventHandler()
        self.dummyEventHandler.setServiceProvider(self.serviceProvider)
        self.dummySensor = GenericEnvironmentSensor()
        self.relayList = (
            GenericRelay(ThermostatState.HEATING),
            GenericRelay(ThermostatState.COOLING),
            GenericRelay(ThermostatState.FAN),
        )
        self.relayMap = {r.function: r for r in self.relayList}
        self.thermostatDriver = Test_Thermostat.TestThermostatDriver(
            localtime=self.localtime,
            sensor=self.dummySensor,
            relays=self.relayList
        )
        self.thermostatDriver.setServiceProvider(self.serviceProvider)
        self.eventBus.processEvents()

    def assertNextTemperature(
            self, temp: float, duration: float, state: ThermostatState):
        self.dummySensor.temperature = temp
        self.now += duration
        self.eventBus.processEvents(self.now)
        self.assertEqual(self.thermostatDriver.state, state)
        for relay in self.relayMap.values():
            if relay.function == state:
                self.assertFalse(
                    relay.isOpen,
                    f"Relay {state} should be closed for state {state}")
            elif relay.function == ThermostatState.FAN and \
                    state.shouldAlsoRunFan:
                self.assertFalse(
                    relay.isOpen,
                    f"Relay FAN should be closed for state {state}")
            elif relay.function == ThermostatState.FAN:
                pass
        if state == ThermostatState.FAN:
            self.assertFalse(
                self.relayMap[ThermostatState.FAN].isOpen,
                "Relay FAN should be closed for state FAN")
            self.assertTrue(
                self.relayMap[ThermostatState.COOLING].isOpen,
                "Relay COOLING should be open for state OFF")
            self.assertTrue(
                self.relayMap[ThermostatState.HEATING].isOpen,
                "Relay HEATING should be open for state OFF")
        if state == ThermostatState.OFF:
            self.assertTrue(
                self.relayMap[ThermostatState.FAN].isOpen,
                "Relay FAN should be open for state OFF")
            self.assertTrue(
                self.relayMap[ThermostatState.COOLING].isOpen,
                "Relay COOLING should be open for state OFF")
            self.assertTrue(
                self.relayMap[ThermostatState.HEATING].isOpen,
                "Relay HEATING should be open for state OFF")

    def test_stateChangedCooling(self):
        self.settings.mode = Settings.Mode.COOL

        self.assertIsNone(self.dummyEventHandler.lastState)
        self.assertNextTemperature(78.0, 15, ThermostatState.COOLING)
        self.eventBus.processEvents()
        self.assertIsNotNone(self.dummyEventHandler.lastState)
        self.assertEqual(
            self.dummyEventHandler.lastState, ThermostatState.COOLING)

    def test_stateChangedHeating(self):
        self.settings.mode = Settings.Mode.HEAT

        self.assertIsNone(self.dummyEventHandler.lastState)
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)
        self.eventBus.processEvents()
        self.assertIsNotNone(self.dummyEventHandler.lastState)
        self.assertEqual(
            self.dummyEventHandler.lastState, ThermostatState.HEATING)

    def test_stateChangedHeatToOff(self):
        self.settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.settings.mode = Settings.Mode.OFF
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 100, ThermostatState.OFF)

    def test_stateChangedAutoHeatToOff(self):
        self.settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.settings.mode = Settings.Mode.OFF
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 100, ThermostatState.OFF)

    def test_stateChangedCoolToOff(self):
        self.settings.mode = Settings.Mode.COOL
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.settings.mode = Settings.Mode.OFF
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 100, ThermostatState.OFF)

    def test_stateChangedAutoCoolToOff(self):
        self.settings.mode = Settings.Mode.AUTO
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.settings.mode = Settings.Mode.OFF
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 100, ThermostatState.OFF)

    def test_stateChangedHeatToCool(self):
        self.settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.settings.mode = Settings.Mode.COOL
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 100, ThermostatState.OFF)

    def test_stateChangedCoolToHeat(self):
        self.settings.mode = Settings.Mode.COOL
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 100, ThermostatState.OFF)

    def test_simpleCool(self):
        self.settings.mode = Settings.Mode.COOL

        self.assertNextTemperature(75.0, 15, ThermostatState.OFF)
        self.assertNextTemperature(78.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, 15, ThermostatState.FAN)
        self.assertNextTemperature(73.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(73.0, 1000, ThermostatState.OFF)

    def test_simpleHeat(self):
        self.settings.mode = Settings.Mode.HEAT

        self.assertNextTemperature(68.0, 15, ThermostatState.OFF)
        self.assertNextTemperature(65.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(68.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(70.0, 15, ThermostatState.FAN)
        self.assertNextTemperature(70.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(70.0, 1000, ThermostatState.OFF)

    def test_simpleAuto(self):
        self.settings.mode = Settings.Mode.AUTO

        self.assertNextTemperature(75.0, 15, ThermostatState.OFF)
        self.assertNextTemperature(78.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, 15, ThermostatState.FAN)
        self.assertNextTemperature(73.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(68.0, 1000, ThermostatState.OFF)
        self.assertNextTemperature(65.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(68.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(70.0, 15, ThermostatState.FAN)
        self.assertNextTemperature(70.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(70.0, 1000, ThermostatState.OFF)

    def test_coolingRunoutCooling(self):
        self.settings.mode = Settings.Mode.AUTO

        self.assertNextTemperature(75.0, 5, ThermostatState.OFF)
        self.assertNextTemperature(76.0, 5, ThermostatState.OFF)
        self.assertNextTemperature(77.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(78.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(78.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(77.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(76.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, 5, ThermostatState.FAN)
        self.assertNextTemperature(73.0, 5, ThermostatState.FAN)
        self.assertNextTemperature(78.0, 5, ThermostatState.COOLING)

    def test_autoOffCooling(self):
        self.settings.mode = Settings.Mode.AUTO

        self.assertNextTemperature(75.0, 5, ThermostatState.OFF)
        self.assertNextTemperature(76.0, 5, ThermostatState.OFF)
        self.assertNextTemperature(77.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(78.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(78.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(77.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(76.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, 5, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, 5, ThermostatState.FAN)
        self.assertNextTemperature(73.0, 100, ThermostatState.OFF)
        self.assertNextTemperature(77.0, 5, ThermostatState.COOLING)

    def test_autoOffToHeating(self):
        self.settings.mode = Settings.Mode.AUTO

        self.assertNextTemperature(69.0, 5, ThermostatState.OFF)
        self.assertNextTemperature(68.0, 5, ThermostatState.OFF)
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)
        self.assertNextTemperature(73.0, 5, ThermostatState.FAN)
        self.assertNextTemperature(73.0, 100, ThermostatState.OFF)

    def test_coolingToHeating(self):
        self.settings.mode = Settings.Mode.AUTO

        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)
        self.assertNextTemperature(78, 5, ThermostatState.COOLING)

    def test_heatingToCooling(self):
        self.settings.mode = Settings.Mode.AUTO

        self.assertNextTemperature(78, 5, ThermostatState.COOLING)
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)

    def test_offToFan(self):
        self.settings.mode = Settings.Mode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)

    def test_fanToHeatingInHeating(self):
        self.settings.mode = Settings.Mode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)
        self.settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)

    def test_fanToHeatingInAuto(self):
        self.settings.mode = Settings.Mode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)
        self.settings.mode = Settings.Mode.AUTO
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)

    def test_fanToOff(self):
        self.settings.mode = Settings.Mode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)
        self.settings.mode = Settings.Mode.OFF
        self.assertNextTemperature(66.9, 5, ThermostatState.OFF)

    def test_heatToFan(self):
        self.settings.mode = Settings.Mode.HEAT

        self.assertNextTemperature(50, 5, ThermostatState.HEATING)
        self.settings.mode = Settings.Mode.FAN
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.FAN)

    def test_heatToOff(self):
        self.settings.mode = Settings.Mode.HEAT

        self.assertNextTemperature(50, 5, ThermostatState.HEATING)
        self.settings.mode = Settings.Mode.OFF
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.OFF)

    def test_coolToFan(self):
        self.settings.mode = Settings.Mode.COOL

        self.assertNextTemperature(90, 5, ThermostatState.COOLING)
        self.settings.mode = Settings.Mode.FAN
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.FAN)

    def test_coolToOff(self):
        self.settings.mode = Settings.Mode.COOL

        self.assertNextTemperature(90, 5, ThermostatState.COOLING)
        self.settings.mode = Settings.Mode.OFF
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.OFF)
