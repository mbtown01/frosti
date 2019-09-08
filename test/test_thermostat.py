import unittest

from src.events import EventBus, EventHandler
from src.settings import settings, Settings
from src.thermostat import ThermostatDriver, ThermostatState, \
    TemperatureChangedEvent, ThermostatStateChangedEvent


class Test_Thermostat(unittest.TestCase):

    class DummyEventHandler(EventHandler):
        def __init__(self, eventBus: EventBus):
            super().__init__(eventBus)
            super()._subscribe(
                ThermostatStateChangedEvent, self._thermostatStateChanged)

            self.__lastState = None

        @property
        def lastState(self):
            return self.__lastState

        def _thermostatStateChanged(self, event: ThermostatStateChangedEvent):
            self.__lastState = event.state

    def setup_method(self, method):
        self.eventBus = EventBus()
        settings.mode = Settings.Mode.COOL
        settings.comfortMin = 68.0
        settings.comfortMax = 75.0
        settings.delta = 1.0
        settings.setEventBus(self.eventBus)

        self.dummyEventHandler = \
            Test_Thermostat.DummyEventHandler(self.eventBus)
        self.thermostatDriver = ThermostatDriver(self.eventBus)
        self.thermostatDriver.processEvents()

    def assertNextTemperature(self, temp: float, state: ThermostatState):
        self.eventBus.put(TemperatureChangedEvent(temp))
        self.thermostatDriver.processEvents()
        self.assertEqual(self.thermostatDriver.state, state)

    def test_stateChangedCooling(self):
        settings.mode = Settings.Mode.COOL

        self.assertIsNone(self.dummyEventHandler.lastState)
        self.assertNextTemperature(78.0, ThermostatState.COOLING)
        self.dummyEventHandler.processEvents()
        self.assertIsNotNone(self.dummyEventHandler.lastState)
        self.assertEqual(
            self.dummyEventHandler.lastState, ThermostatState.COOLING)

    def test_stateChangedHeating(self):
        settings.mode = Settings.Mode.HEAT

        self.assertIsNone(self.dummyEventHandler.lastState)
        self.assertNextTemperature(60.0, ThermostatState.HEATING)
        self.dummyEventHandler.processEvents()
        self.assertIsNotNone(self.dummyEventHandler.lastState)
        self.assertEqual(
            self.dummyEventHandler.lastState, ThermostatState.HEATING)

    def test_stateChangedHeatToOff(self):
        settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(60.0, ThermostatState.HEATING)

        settings.mode = Settings.Mode.OFF
        self.assertNextTemperature(60.0, ThermostatState.OFF)

    def test_stateChangedHeatToCool(self):
        settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(60.0, ThermostatState.HEATING)

        settings.mode = Settings.Mode.COOL
        self.assertNextTemperature(60.0, ThermostatState.OFF)

    def test_stateChangedCoolToHeat(self):
        settings.mode = Settings.Mode.COOL
        self.assertNextTemperature(80.0, ThermostatState.COOLING)

        settings.mode = Settings.Mode.HEAT
        self.assertNextTemperature(80.0, ThermostatState.OFF)

    def test_simpleCool(self):
        settings.mode = Settings.Mode.COOL

        self.assertNextTemperature(75.0, ThermostatState.OFF)
        self.assertNextTemperature(78.0, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, ThermostatState.OFF)

    def test_simpleHeat(self):
        settings.mode = Settings.Mode.HEAT

        self.assertNextTemperature(68.0, ThermostatState.OFF)
        self.assertNextTemperature(65.0, ThermostatState.HEATING)
        self.assertNextTemperature(68.0, ThermostatState.HEATING)
        self.assertNextTemperature(70.0, ThermostatState.OFF)

    def test_simpleAuto(self):
        settings.mode = Settings.Mode.AUTO

        self.assertNextTemperature(75.0, ThermostatState.OFF)
        self.assertNextTemperature(78.0, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, ThermostatState.OFF)
        self.assertNextTemperature(68.0, ThermostatState.OFF)
        self.assertNextTemperature(65.0, ThermostatState.HEATING)
        self.assertNextTemperature(68.0, ThermostatState.HEATING)
        self.assertNextTemperature(70.0, ThermostatState.OFF)
