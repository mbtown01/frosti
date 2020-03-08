import unittest
from time import mktime, strptime

from src.core import EventBus, EventBusMember, ServiceProvider, ThermostatState
from src.services import ConfigService
from src.services import SettingsService
from src.core.events import ThermostatStateChangedEvent
from src.core.generics import GenericLcdDisplay, GenericEnvironmentSensor, \
    GenericRelay
from src.services import ThermostatService


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

    class DummyEventBusMember(EventBusMember):
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

    class TestThermostatDriver(ThermostatService):

        def __init__(self,
                     sensor: GenericEnvironmentSensor,
                     relays: list):

            super().__init__(
                lcd=GenericLcdDisplay(20, 4),
                sensor=sensor,
                relays=relays
            )

    def setup_method(self, method):
        # This is a Tuesday FYI, day '1' of 7 [0-6]
        # All tests should be in the 'away' program above
        self.serviceProvider = ServiceProvider()
        testTime = strptime('01/01/19 08:01:00', '%m/%d/%y %H:%M:%S')
        self.eventBus = EventBus(now=mktime(testTime))
        self.serviceProvider.installService(EventBus, self.eventBus)
        self.config = ConfigService()
        self.serviceProvider.installService(ConfigService, self.config)
        self.settings = SettingsService(json)
        self.settings.setServiceProvider(self.serviceProvider)
        self.serviceProvider.installService(SettingsService, self.settings)
        self.settings.mode = SettingsService.Mode.COOL

        self.dummyEventBusMember = \
            Test_Thermostat.DummyEventBusMember()
        self.dummyEventBusMember.setServiceProvider(self.serviceProvider)
        self.dummySensor = GenericEnvironmentSensor()
        self.relayList = (
            GenericRelay(ThermostatState.HEATING),
            GenericRelay(ThermostatState.COOLING),
            GenericRelay(ThermostatState.FAN),
        )
        self.relayMap = {r.function: r for r in self.relayList}
        self.thermostatDriver = Test_Thermostat.TestThermostatDriver(
            sensor=self.dummySensor,
            relays=self.relayList
        )
        self.thermostatDriver.setServiceProvider(self.serviceProvider)
        self.eventBus.processEvents()

    def assertNextTemperature(
            self, temp: float, duration: float, state: ThermostatState):
        self.dummySensor.temperature = temp
        self.eventBus.processEvents(now=self.eventBus.now+duration)
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
        self.settings.mode = SettingsService.Mode.COOL

        self.assertIsNone(self.dummyEventBusMember.lastState)
        self.assertNextTemperature(78.0, 15, ThermostatState.COOLING)
        self.eventBus.processEvents()
        self.assertIsNotNone(self.dummyEventBusMember.lastState)
        self.assertEqual(
            self.dummyEventBusMember.lastState, ThermostatState.COOLING)

    def test_stateChangedHeating(self):
        self.settings.mode = SettingsService.Mode.HEAT

        self.assertIsNone(self.dummyEventBusMember.lastState)
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)
        self.eventBus.processEvents()
        self.assertIsNotNone(self.dummyEventBusMember.lastState)
        self.assertEqual(
            self.dummyEventBusMember.lastState, ThermostatState.HEATING)

    def test_stateChangedHeatToOff(self):
        self.settings.mode = SettingsService.Mode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.settings.mode = SettingsService.Mode.OFF
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 100, ThermostatState.OFF)

    def test_stateChangedAutoHeatToOff(self):
        self.settings.mode = SettingsService.Mode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.settings.mode = SettingsService.Mode.OFF
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 100, ThermostatState.OFF)

    def test_stateChangedCoolToOff(self):
        self.settings.mode = SettingsService.Mode.COOL
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.settings.mode = SettingsService.Mode.OFF
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 100, ThermostatState.OFF)

    def test_stateChangedAutoCoolToOff(self):
        self.settings.mode = SettingsService.Mode.AUTO
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.settings.mode = SettingsService.Mode.OFF
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 100, ThermostatState.OFF)

    def test_stateChangedHeatToCool(self):
        self.settings.mode = SettingsService.Mode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.settings.mode = SettingsService.Mode.COOL
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 100, ThermostatState.OFF)

    def test_stateChangedHeatToCoolPlusNewTargets(self):
        self.settings.mode = SettingsService.Mode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.settings.mode = SettingsService.Mode.COOL
        self.settings.comfortMin = 50.0
        self.settings.comfortMax = 45.0
        self.assertNextTemperature(60.0, 30, ThermostatState.COOLING)
        self.assertNextTemperature(40.0, 30, ThermostatState.FAN)
        self.assertNextTemperature(40.0, 100, ThermostatState.OFF)

    def test_stateChangedCoolToHeat(self):
        self.settings.mode = SettingsService.Mode.COOL
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.settings.mode = SettingsService.Mode.HEAT
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 100, ThermostatState.OFF)

    def test_stateChangedCoolToHeatPlusNewTargets(self):
        self.settings.mode = SettingsService.Mode.COOL
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.settings.mode = SettingsService.Mode.HEAT
        self.settings.comfortMin = 85.0
        self.settings.comfortMax = 90.0
        self.assertNextTemperature(80.0, 30, ThermostatState.HEATING)
        self.assertNextTemperature(95.0, 30, ThermostatState.FAN)
        self.assertNextTemperature(95.0, 100, ThermostatState.OFF)

    def test_simpleCool(self):
        self.settings.mode = SettingsService.Mode.COOL

        self.assertNextTemperature(75.0, 15, ThermostatState.OFF)
        self.assertNextTemperature(78.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, 15, ThermostatState.FAN)
        self.assertNextTemperature(73.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(73.0, 1000, ThermostatState.OFF)

    def test_simpleHeat(self):
        self.settings.mode = SettingsService.Mode.HEAT

        self.assertNextTemperature(68.0, 15, ThermostatState.OFF)
        self.assertNextTemperature(65.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(68.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(70.0, 15, ThermostatState.FAN)
        self.assertNextTemperature(70.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(70.0, 1000, ThermostatState.OFF)

    def test_simpleAuto(self):
        self.settings.mode = SettingsService.Mode.AUTO

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
        self.settings.mode = SettingsService.Mode.AUTO

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
        self.settings.mode = SettingsService.Mode.AUTO

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
        self.settings.mode = SettingsService.Mode.AUTO

        self.assertNextTemperature(69.0, 5, ThermostatState.OFF)
        self.assertNextTemperature(68.0, 5, ThermostatState.OFF)
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)
        self.assertNextTemperature(73.0, 5, ThermostatState.FAN)
        self.assertNextTemperature(73.0, 100, ThermostatState.OFF)

    def test_coolingToHeating(self):
        self.settings.mode = SettingsService.Mode.AUTO

        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)
        self.assertNextTemperature(78, 5, ThermostatState.COOLING)

    def test_heatingToCooling(self):
        self.settings.mode = SettingsService.Mode.AUTO

        self.assertNextTemperature(78, 5, ThermostatState.COOLING)
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)

    def test_offToFan(self):
        self.settings.mode = SettingsService.Mode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)

    def test_fanToHeatingInHeating(self):
        self.settings.mode = SettingsService.Mode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)
        self.settings.mode = SettingsService.Mode.HEAT
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)

    def test_fanToHeatingInAuto(self):
        self.settings.mode = SettingsService.Mode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)
        self.settings.mode = SettingsService.Mode.AUTO
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)

    def test_fanToOff(self):
        self.settings.mode = SettingsService.Mode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)
        self.settings.mode = SettingsService.Mode.OFF
        self.assertNextTemperature(66.9, 30, ThermostatState.OFF)

    def test_heatToFan(self):
        self.settings.mode = SettingsService.Mode.HEAT

        self.assertNextTemperature(50, 5, ThermostatState.HEATING)
        self.settings.mode = SettingsService.Mode.FAN
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.FAN)

    def test_heatToOff(self):
        self.settings.mode = SettingsService.Mode.HEAT

        self.assertNextTemperature(50, 5, ThermostatState.HEATING)
        self.settings.mode = SettingsService.Mode.OFF
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.OFF)

    def test_coolToFan(self):
        self.settings.mode = SettingsService.Mode.COOL

        self.assertNextTemperature(90, 5, ThermostatState.COOLING)
        self.settings.mode = SettingsService.Mode.FAN
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.FAN)

    def test_coolToOff(self):
        self.settings.mode = SettingsService.Mode.COOL

        self.assertNextTemperature(90, 5, ThermostatState.COOLING)
        self.settings.mode = SettingsService.Mode.OFF
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.OFF)
