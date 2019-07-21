import unittest
from queue import Queue

from src.events import Event, EventBus, EventHandler
from src.settings import Settings, SettingsChangedEvent
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
        self.dummyEventHandler = \
            Test_Thermostat.DummyEventHandler(self.eventBus)
        self.thermostatDriver = ThermostatDriver(self.eventBus)
        self.thermostatDriver.processEvents()

    def assertNextTemperature(self, temp: float, state: ThermostatState):
        self.eventBus.put(TemperatureChangedEvent(temp))
        self.thermostatDriver.processEvents()
        self.assertEqual(self.thermostatDriver.state, state)

    def test_settings(self):
        settings = Settings(Settings.Mode.COOL, 68.0, 75.0, 1.0)

        self.assertIsNone(self.thermostatDriver.settings)
        self.eventBus.put(SettingsChangedEvent(settings))
        self.thermostatDriver.processEvents()

        self.assertIsNotNone(self.thermostatDriver.settings)
        self.assertEqual(settings.mode, self.thermostatDriver.settings.mode)

    def test_noSettings(self):
        with self.assertRaises(RuntimeError):
            self.assertNextTemperature(78.0, ThermostatState.COOLING)

    def test_stateChangedCooling(self):
        settings = Settings(Settings.Mode.COOL, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))

        self.assertIsNone(self.dummyEventHandler.lastState)
        self.assertNextTemperature(78.0, ThermostatState.COOLING)
        self.dummyEventHandler.processEvents()
        self.assertIsNotNone(self.dummyEventHandler.lastState)
        self.assertEqual(
            self.dummyEventHandler.lastState, ThermostatState.COOLING)

    def test_stateChangedHeating(self):
        settings = Settings(Settings.Mode.HEAT, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))

        self.assertIsNone(self.dummyEventHandler.lastState)
        self.assertNextTemperature(60.0, ThermostatState.HEATING)
        self.dummyEventHandler.processEvents()
        self.assertIsNotNone(self.dummyEventHandler.lastState)
        self.assertEqual(
            self.dummyEventHandler.lastState, ThermostatState.HEATING)

    def test_stateChangedHeatToOff(self):
        settings = Settings(Settings.Mode.HEAT, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))
        self.assertNextTemperature(60.0, ThermostatState.HEATING)

        settings = Settings(Settings.Mode.OFF, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))
        self.assertNextTemperature(60.0, ThermostatState.OFF)

    def test_stateChangedHeatToCool(self):
        settings = Settings(Settings.Mode.HEAT, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))
        self.assertNextTemperature(60.0, ThermostatState.HEATING)

        settings = Settings(Settings.Mode.COOL, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))
        self.assertNextTemperature(60.0, ThermostatState.OFF)

    def test_stateChangedCoolToHeat(self):
        settings = Settings(Settings.Mode.COOL, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))
        self.assertNextTemperature(80.0, ThermostatState.COOLING)

        settings = Settings(Settings.Mode.HEAT, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))
        self.assertNextTemperature(80.0, ThermostatState.OFF)

    def test_simpleCool(self):
        settings = Settings(Settings.Mode.COOL, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))

        self.assertNextTemperature(75.0, ThermostatState.OFF)
        self.assertNextTemperature(78.0, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, ThermostatState.OFF)

    def test_simpleHeat(self):
        settings = Settings(Settings.Mode.HEAT, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))

        self.assertNextTemperature(68.0, ThermostatState.OFF)
        self.assertNextTemperature(65.0, ThermostatState.HEATING)
        self.assertNextTemperature(68.0, ThermostatState.HEATING)
        self.assertNextTemperature(70.0, ThermostatState.OFF)

    def test_simpleAuto(self):
        settings = Settings(Settings.Mode.AUTO, 68.0, 75.0, 1.0)
        self.eventBus.put(SettingsChangedEvent(settings))

        self.assertNextTemperature(75.0, ThermostatState.OFF)
        self.assertNextTemperature(78.0, ThermostatState.COOLING)
        self.assertNextTemperature(75.0, ThermostatState.COOLING)
        self.assertNextTemperature(73.0, ThermostatState.OFF)
        self.assertNextTemperature(68.0, ThermostatState.OFF)
        self.assertNextTemperature(65.0, ThermostatState.HEATING)
        self.assertNextTemperature(68.0, ThermostatState.HEATING)
        self.assertNextTemperature(70.0, ThermostatState.OFF)
