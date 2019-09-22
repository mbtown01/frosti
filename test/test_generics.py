import unittest

from src.events import EventBus, EventHandler
from src.generics import GenericLcdDisplay, GenericEnvironmentSensor, \
    GenericButton, GenericThermostatDriver, CounterBasedInvoker, \
    GenericRelay, ThermostatState, ThermostatStateChangedEvent, \
    TemperatureChangedEvent


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


class Test_CounterBasedInvoker(unittest.TestCase):

    def setup_method(self, method):
        self.__invokeCountFoo = 0
        self.__invokeCountBar = 0

    def invoke_foo(self):
        self.__invokeCountFoo += 1

    def invoke_bar(self):
        self.__invokeCountBar += 1

    def test_invoke_simple(self):
        invoker = CounterBasedInvoker(2, [self.invoke_foo])
        self.assertEqual(0, self.__invokeCountFoo)
        invoker.increment()
        self.assertEqual(0, self.__invokeCountFoo)
        invoker.increment()
        self.assertEqual(1, self.__invokeCountFoo)

    def test_invoke_list(self):
        invoker = CounterBasedInvoker(2, [self.invoke_foo, self.invoke_bar])
        self.assertEqual(0, self.__invokeCountFoo)
        self.assertEqual(0, self.__invokeCountBar)
        invoker.increment()
        self.assertEqual(0, self.__invokeCountFoo)
        self.assertEqual(0, self.__invokeCountBar)
        invoker.increment()
        self.assertEqual(1, self.__invokeCountFoo)
        self.assertEqual(0, self.__invokeCountBar)
        invoker.increment()
        self.assertEqual(1, self.__invokeCountFoo)
        self.assertEqual(0, self.__invokeCountBar)
        invoker.increment()
        self.assertEqual(1, self.__invokeCountFoo)
        self.assertEqual(1, self.__invokeCountBar)

    def test_force_invoke(self):
        invoker = CounterBasedInvoker(2, [self.invoke_foo])
        self.assertEqual(0, self.__invokeCountFoo)
        invoker.invokeCurrent()
        self.assertEqual(1, self.__invokeCountFoo)
        invoker.increment()
        self.assertEqual(1, self.__invokeCountFoo)
        invoker.increment()
        self.assertEqual(2, self.__invokeCountFoo)

    def test_reset(self):
        invoker = CounterBasedInvoker(2, [self.invoke_foo, self.invoke_bar])
        self.assertEqual(0, self.__invokeCountFoo)
        self.assertEqual(0, self.__invokeCountBar)
        invoker.increment()
        invoker.increment()
        self.assertEqual(1, self.__invokeCountFoo)
        self.assertEqual(0, self.__invokeCountBar)
        invoker.reset()
        invoker.increment()
        invoker.increment()
        self.assertEqual(2, self.__invokeCountFoo)
        self.assertEqual(0, self.__invokeCountBar)


class Test_GenericHardwareDriver(unittest.TestCase):

    class DummyEventHandler(EventHandler):
        def __init__(self, eventBus: EventBus):
            super().__init__(eventBus)
            super()._subscribe(
                ThermostatStateChangedEvent, self._thermostatStateChanged)
            super()._subscribe(
                TemperatureChangedEvent, self._temperatureChanged)

            self.__lastState = None
            self.__lastTemperature = None

        @property
        def lastState(self):
            return self.__lastState

        @property
        def lastTemperature(self):
            return self.__lastTemperature

        def _thermostatStateChanged(self, event: ThermostatStateChangedEvent):
            self.__lastState = event.state

        def _temperatureChanged(self, event: TemperatureChangedEvent):
            self.__lastTemperature = event.value

    def setup_method(self, method):
        self.__eventBus = EventBus()
        self.__dummyEventHandler = \
            Test_GenericHardwareDriver.DummyEventHandler(self.__eventBus)
        self.__environmentSensor = GenericEnvironmentSensor()
        self.__display = GenericLcdDisplay(20, 4)
        self.__buttonMap = {
            'up': GenericButton(1),
            'down': GenericButton(2),
            'enter': GenericButton(3),
            'mode': GenericButton(4),
        }
        self.__relayList = (
            GenericRelay(ThermostatState.HEATING),
            GenericRelay(ThermostatState.COOLING),
            GenericRelay(ThermostatState.FAN),
        )
        self.__relayMap = {r.function: r for r in self.__relayList}

        self.__hardwareDriver = GenericThermostatDriver(
            eventBus=self.__eventBus,
            loopSleep=0.1,
            lcd=self.__display,
            sensor=self.__environmentSensor,
            buttons=self.__buttonMap.values(),
            relays=self.__relayList
        )

    def test_simple(self):
        self.__hardwareDriver.processEvents()
        self.__dummyEventHandler.processEvents()

        self.assertEqual(
            self.__environmentSensor.temperature,
            self.__dummyEventHandler.lastTemperature)
