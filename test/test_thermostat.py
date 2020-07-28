import unittest
import yaml
from time import mktime, strptime

from src.core import EventBus, ServiceConsumer, ServiceProvider, \
    ThermostatState, ThermostatMode
from src.services import ThermostatService, RelayManagementService, \
    OrmManagementService
from src.core.events import ThermostatStateChangedEvent, SensorDataChangedEvent


yamlText = """
config:
    thermostat.delta: 1.0
    thermostat.fanRunoutDuration: 30
    thermostat.timezone: "America/Chicago"
    ui.backlightTimeout: 10

programs:
    home:
        comfortMin: 70
        comfortMax: 76
        priceOverrides:
            - { price: 0.50, comfortMax: 80 }
            - { price: 1.00, comfortMax: 88 }
    away:
        comfortMin: 68
        comfortMax: 75
        priceOverrides:
            - { price: 0.25, comfortMax: 82 }
schedule:
    work week:
        days: [0, 1, 2, 3, 4]
        times:
            - { hour: 8, minute: 0, program: away }
            - { hour: 17, minute: 0, program: home }
    weekend:
        days: [5, 6]
        times:
            - { hour: 8, minute: 0, program: home }
            - { hour: 20, minute: 0, program: away }
"""


# TODO: Defaults and current time/price configuration are different,
# check that startup sequence doesn't short-cycle the AC/HEAT

class Test_Thermostat(unittest.TestCase):

    class DummyServiceConsumer(ServiceConsumer):
        def __init__(self):
            self.__lastState = None

        def setServiceProvider(self, provider: ServiceProvider):
            super().setServiceProvider(provider)

            eventBus = self._getService(EventBus)
            eventBus.installEventHandler(
                ThermostatStateChangedEvent, self._thermostatStateChanged)

        @property
        def lastState(self):
            return self.__lastState

        def _thermostatStateChanged(self, event: ThermostatStateChangedEvent):
            self.__lastState = event.state

    def setup_method(self, method):
        # This is a Tuesday FYI, day '1' of 7 [0-6], built manually in UTC
        # time to represent 8:01 AM in the America/Chicago time zone
        # All tests should be in the 'away' program above
        testTime = strptime('01/01/19 14:01:00', '%m/%d/%y %H:%M:%S')
        self.serviceProvider = ServiceProvider()
        self.eventBus = EventBus(now=mktime(testTime))
        self.serviceProvider.installService(EventBus, self.eventBus)
        self.relayManagement = RelayManagementService()
        self.relayManagement.setServiceProvider(self.serviceProvider)
        self.serviceProvider.installService(
            RelayManagementService, self.relayManagement)
        self.ormManagementService = OrmManagementService(isTestInstance=True)
        self.ormManagementService.setServiceProvider(self.serviceProvider)
        self.ormManagementService.importFromDict(
            yaml.load(yamlText, Loader=yaml.FullLoader))
        self.serviceProvider.installService(
            OrmManagementService, self.ormManagementService)
        self.thermostat = ThermostatService()
        self.thermostat.setServiceProvider(self.serviceProvider)
        self.thermostat.mode = ThermostatMode.COOL

        self.dummyEventBusMember = \
            Test_Thermostat.DummyServiceConsumer()
        self.dummyEventBusMember.setServiceProvider(self.serviceProvider)
        self.eventBus.processEvents()

    def assertNextTemperature(
            self, temp: float, duration: float, state: ThermostatState):
        self.eventBus.fireEvent(SensorDataChangedEvent(
            temperature=temp, pressure=1000.0, humidity=50.0))
        self.eventBus.processEvents(now=self.eventBus.now)
        self.eventBus.processEvents(now=self.eventBus.now + duration)
        self.assertEqual(self.thermostat.state, state)

        states = [
            ThermostatState.COOLING,
            ThermostatState.HEATING,
            ThermostatState.FAN
        ]
        for checkState in states:
            if checkState == state:
                self.assertFalse(
                    self.relayManagement.getRelayStatus(checkState),
                    f"Relay {state} should be closed for state {state}")
            elif checkState == ThermostatState.FAN and \
                    state.shouldAlsoRunFan:
                self.assertFalse(
                    self.relayManagement.getRelayStatus(checkState),
                    f"Relay FAN should be closed for state {state}")
            elif checkState == ThermostatState.FAN:
                pass

        if state == ThermostatState.FAN:
            self.assertFalse(
                self.relayManagement.getRelayStatus(ThermostatState.FAN),
                "Relay FAN should be closed for state FAN")
            self.assertTrue(
                self.relayManagement.getRelayStatus(ThermostatState.COOLING),
                "Relay COOLING should be open for state OFF")
            self.assertTrue(
                self.relayManagement.getRelayStatus(ThermostatState.HEATING),
                "Relay HEATING should be open for state OFF")
        if state == ThermostatState.OFF:
            self.assertTrue(
                self.relayManagement.getRelayStatus(ThermostatState.FAN),
                "Relay FAN should be open for state OFF")
            self.assertTrue(
                self.relayManagement.getRelayStatus(ThermostatState.COOLING),
                "Relay COOLING should be open for state OFF")
            self.assertTrue(
                self.relayManagement.getRelayStatus(ThermostatState.HEATING),
                "Relay HEATING should be open for state OFF")

    def test_stateChangedCooling(self):
        self.thermostat.mode = ThermostatMode.COOL

        self.assertIsNone(self.dummyEventBusMember.lastState)
        self.assertNextTemperature(78.0, 15, ThermostatState.COOLING)
        self.eventBus.processEvents()
        self.assertIsNotNone(self.dummyEventBusMember.lastState)
        self.assertEqual(
            self.dummyEventBusMember.lastState, ThermostatState.COOLING)

    def test_stateChangedHeating(self):
        self.thermostat.mode = ThermostatMode.HEAT

        self.assertIsNone(self.dummyEventBusMember.lastState)
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)
        self.eventBus.processEvents()
        self.assertIsNotNone(self.dummyEventBusMember.lastState)
        self.assertEqual(
            self.dummyEventBusMember.lastState, ThermostatState.HEATING)

    def test_stateChangedHeatToOff(self):
        self.thermostat.mode = ThermostatMode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.thermostat.mode = ThermostatMode.OFF
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 100, ThermostatState.OFF)

    def test_stateChangedAutoHeatToOff(self):
        self.thermostat.mode = ThermostatMode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.thermostat.mode = ThermostatMode.OFF
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 100, ThermostatState.OFF)

    def test_stateChangedCoolToOff(self):
        self.thermostat.mode = ThermostatMode.COOL
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.thermostat.mode = ThermostatMode.OFF
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 100, ThermostatState.OFF)

    def test_stateChangedAutoCoolToOff(self):
        self.thermostat.mode = ThermostatMode.AUTO
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.thermostat.mode = ThermostatMode.OFF
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 100, ThermostatState.OFF)

    def test_stateChangedHeatToCool(self):
        self.thermostat.mode = ThermostatMode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.thermostat.mode = ThermostatMode.COOL
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(60.0, 100, ThermostatState.OFF)

    def test_stateChangedHeatToCoolPlusNewTargets(self):
        self.thermostat.mode = ThermostatMode.HEAT
        self.assertNextTemperature(60.0, 15, ThermostatState.HEATING)

        self.thermostat.mode = ThermostatMode.COOL
        self.thermostat.comfortMin = 50.0
        self.thermostat.comfortMax = 45.0
        self.assertNextTemperature(60.0, 30, ThermostatState.COOLING)
        self.assertNextTemperature(40.0, 30, ThermostatState.FAN)
        self.assertNextTemperature(40.0, 100, ThermostatState.OFF)

    def test_stateChangedCoolToHeat(self):
        self.thermostat.mode = ThermostatMode.COOL
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.thermostat.mode = ThermostatMode.HEAT
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 10, ThermostatState.FAN)
        self.assertNextTemperature(80.0, 100, ThermostatState.OFF)

    def test_stateChangedCoolToHeatPlusNewTargets(self):
        self.thermostat.mode = ThermostatMode.COOL
        self.assertNextTemperature(80.0, 15, ThermostatState.COOLING)

        self.thermostat.mode = ThermostatMode.HEAT
        self.thermostat.comfortMin = 85.0
        self.thermostat.comfortMax = 90.0
        self.assertNextTemperature(80.0, 30, ThermostatState.HEATING)
        self.assertNextTemperature(95.0, 30, ThermostatState.FAN)
        self.assertNextTemperature(95.0, 100, ThermostatState.OFF)

    def test_simpleCool(self):
        self.thermostat.mode = ThermostatMode.COOL

        self.assertNextTemperature(75.0, 15, ThermostatState.OFF)
        self.assertNextTemperature(78.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, 15, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, 15, ThermostatState.FAN)
        self.assertNextTemperature(73.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(73.0, 1000, ThermostatState.OFF)

    def test_simpleHeat(self):
        self.thermostat.mode = ThermostatMode.HEAT

        self.assertNextTemperature(68.0, 15, ThermostatState.OFF)
        self.assertNextTemperature(65.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(68.0, 15, ThermostatState.HEATING)
        self.assertNextTemperature(70.0, 15, ThermostatState.FAN)
        self.assertNextTemperature(70.0, 60, ThermostatState.OFF)
        self.assertNextTemperature(70.0, 1000, ThermostatState.OFF)

    def test_simpleAuto(self):
        self.thermostat.mode = ThermostatMode.AUTO

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
        self.thermostat.mode = ThermostatMode.AUTO

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
        self.thermostat.mode = ThermostatMode.AUTO

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
        self.thermostat.mode = ThermostatMode.AUTO

        self.assertNextTemperature(69.0, 5, ThermostatState.OFF)
        self.assertNextTemperature(68.0, 5, ThermostatState.OFF)
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)
        self.assertNextTemperature(73.0, 5, ThermostatState.FAN)
        self.assertNextTemperature(73.0, 100, ThermostatState.OFF)

    def test_coolingToHeating(self):
        self.thermostat.mode = ThermostatMode.AUTO

        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)
        self.assertNextTemperature(78, 5, ThermostatState.COOLING)

    def test_heatingToCooling(self):
        self.thermostat.mode = ThermostatMode.AUTO

        self.assertNextTemperature(78, 5, ThermostatState.COOLING)
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)

    def test_offToFan(self):
        self.thermostat.mode = ThermostatMode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)

    def test_fanToHeatingInHeating(self):
        self.thermostat.mode = ThermostatMode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)
        self.thermostat.mode = ThermostatMode.HEAT
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)

    def test_fanToHeatingInAuto(self):
        self.thermostat.mode = ThermostatMode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)
        self.thermostat.mode = ThermostatMode.AUTO
        self.assertNextTemperature(66.9, 5, ThermostatState.HEATING)

    def test_fanToOff(self):
        self.thermostat.mode = ThermostatMode.FAN

        self.assertNextTemperature(78, 5, ThermostatState.FAN)
        self.thermostat.mode = ThermostatMode.OFF
        self.assertNextTemperature(66.9, 30, ThermostatState.OFF)

    def test_heatToFan(self):
        self.thermostat.mode = ThermostatMode.HEAT

        self.assertNextTemperature(50, 5, ThermostatState.HEATING)
        self.thermostat.mode = ThermostatMode.FAN
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.FAN)

    def test_heatToOff(self):
        self.thermostat.mode = ThermostatMode.HEAT

        self.assertNextTemperature(50, 5, ThermostatState.HEATING)
        self.thermostat.mode = ThermostatMode.OFF
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.OFF)

    def test_coolToFan(self):
        self.thermostat.mode = ThermostatMode.COOL

        self.assertNextTemperature(90, 5, ThermostatState.COOLING)
        self.thermostat.mode = ThermostatMode.FAN
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.FAN)

    def test_coolToOff(self):
        self.thermostat.mode = ThermostatMode.COOL

        self.assertNextTemperature(90, 5, ThermostatState.COOLING)
        self.thermostat.mode = ThermostatMode.OFF
        self.assertNextTemperature(50, 5, ThermostatState.FAN)
        self.assertNextTemperature(50, 10, ThermostatState.FAN)
        self.assertNextTemperature(50, 100, ThermostatState.OFF)
