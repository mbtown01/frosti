import unittest
from time import strptime, mktime

from src.config import Config
from src.core import ServiceProvider
from src.settings import Settings
from src.core import EventBus, EventBusMember, TimerBasedHandler, \
    ThermostatState
from src.core.generics import GenericLcdDisplay, GenericEnvironmentSensor, \
    GenericRelay
from src.core.events import ThermostatStateChangedEvent, SensorDataChangedEvent
from src.services import ThermostatService


class Test_GenericLcdDisplay(unittest.TestCase):

    def setup_method(self, method):
        pass

    def test_row_update_middle(self):
        row = GenericLcdDisplay.Row(20)
        row.update(5, 'test')
        updates = row.commit()

        self.assertEqual(1, len(updates))
        self.assertEqual(5, updates[0][0])
        self.assertEqual('test', updates[0][1])

    def test_row_update_leading(self):
        row = GenericLcdDisplay.Row(20)
        row.update(0, 'easy_update')
        updates = row.commit()

        self.assertEqual(1, len(updates))
        self.assertEqual(0, updates[0][0])
        self.assertEqual('easy_update', updates[0][1])

    def test_row_update_too_long(self):
        row = GenericLcdDisplay.Row(20)
        row.update(0, '0123456789012345678901234567890123456789')
        updates = row.commit()

        self.assertEqual(1, len(updates))
        self.assertEqual(0, updates[0][0])
        self.assertEqual('01234567890123456789', updates[0][1])

    def test_row_update_neg_offset(self):
        row = GenericLcdDisplay.Row(20)
        row.update(-5, '0123456789')
        updates = row.commit()

        self.assertEqual(1, len(updates))
        self.assertEqual(0, updates[0][0])
        self.assertEqual('56789', updates[0][1])

    def test_row_update_two_updates(self):
        row = GenericLcdDisplay.Row(20)
        row.update(0, '01234567890123456789')
        updates = row.commit()
        row.update(0, '01234012340123401234')
        updates = row.commit()

        self.assertEqual(2, len(updates))
        self.assertEqual(5, updates[0][0])
        self.assertEqual('01234', updates[0][1])
        self.assertEqual(15, updates[1][0])
        self.assertEqual('01234', updates[1][1])

    def test_row_update_two_updates_no_finalize(self):
        row = GenericLcdDisplay.Row(20)
        row.update(0, '01234567890123456789')
        row.update(0, '01234012340123401234')
        updates = row.commit()

        self.assertEqual(1, len(updates))
        self.assertEqual(0, updates[0][0])
        self.assertEqual('01234012340123401234', updates[0][1])

    def test_screen_simple(self):
        screen = GenericLcdDisplay(20, 2)
        screen.update(0, 0, "01234567890123456789")
        screen.update(1, 0, "01234567890123456789")
        screen.commit()

        self.assertEqual(20, screen.width)
        self.assertEqual(2, screen.height)
        self.assertEqual(
            "01234567890123456789\n01234567890123456789", screen.text)

    def test_screen_clear(self):
        screen = GenericLcdDisplay(20, 2)
        screen.update(0, 0, "01234567890123456789")
        screen.update(1, 0, "01234567890123456789")
        screen.commit()
        self.assertEqual(
            "01234567890123456789\n01234567890123456789", screen.text)

        screen.clear()
        self.assertEqual(
            "                    \n                    ", screen.text)

    def test_screen_too_many_rows(self):
        screen = GenericLcdDisplay(20, 2)
        with self.assertRaises(RuntimeError):
            screen.update(2, 4, 'this should throw')


class Test_GenericHardwareDriver(unittest.TestCase):

    class DummyEventBusMember(EventBusMember):
        def __init__(self):
            self.__lastState = None
            self.__lastTemperature = None

        def setServiceProvider(self, provider: ServiceProvider):
            super().setServiceProvider(provider)
            super()._installEventHandler(
                ThermostatStateChangedEvent, self.__thermostatStateChanged)
            super()._installEventHandler(
                SensorDataChangedEvent, self.__sensorDataChanged)

        @property
        def lastState(self):
            return self.__lastState

        @property
        def lastTemperature(self):
            return self.__lastTemperature

        def __thermostatStateChanged(self, event: ThermostatStateChangedEvent):
            self.__lastState = event.state

        def __sensorDataChanged(self, event: SensorDataChangedEvent):
            self.__lastTemperature = event.temperature

    def setup_method(self, method):
        self.serviceProvider = ServiceProvider()
        testTime = strptime('01/01/19 08:01:00', '%m/%d/%y %H:%M:%S')
        self.eventBus = EventBus(now=mktime(testTime))
        self.serviceProvider.installService(EventBus, self.eventBus)
        self.config = Config()
        self.serviceProvider.installService(Config, self.config)
        self.settings = Settings()
        self.settings.setServiceProvider(self.serviceProvider)
        self.serviceProvider.installService(Settings, self.settings)

        self.dummyEventBusMember = \
            Test_GenericHardwareDriver.DummyEventBusMember()
        self.dummyEventBusMember.setServiceProvider(self.serviceProvider)
        self.environmentSensor = GenericEnvironmentSensor()
        self.display = GenericLcdDisplay(20, 4)
        self.relayList = (
            GenericRelay(ThermostatState.HEATING),
            GenericRelay(ThermostatState.COOLING),
            GenericRelay(ThermostatState.FAN),
        )

        self.hardwareDriver = ThermostatService(
            lcd=self.display,
            sensor=self.environmentSensor,
            relays=self.relayList
        )
        self.hardwareDriver.setServiceProvider(self.serviceProvider)
        self.eventBus.processEvents()

    def test_simple(self):
        self.eventBus.processEvents(now=self.eventBus.now+100.0)

        self.assertEqual(
            self.environmentSensor.temperature,
            self.dummyEventBusMember.lastTemperature)
