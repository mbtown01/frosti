import unittest
from threading import Timer
from time import time

from src.core import Event, EventBus, ServiceConsumer, ServiceProvider


class Test_EventBus(unittest.TestCase):

    class DummyEvent(Event):
        def __init__(self, test: int):
            super().__init__('DummyEvent', {'test': test})

        @property
        def test(self):
            return super().data['test']

    class DummyServiceConsumer(ServiceConsumer):
        def __init__(self):
            self.eventCount = 0

        def setServiceProvider(self, provider: ServiceProvider):
            super().setServiceProvider(provider)

            eventBus = self._getService(EventBus)
            eventBus.installEventHandler(
                Test_EventBus.DummyEvent, self.__processDummyEvent)

        def __processDummyEvent(self, event: Event):
            self.eventCount += 1

    def setup_method(self, method):
        self.serviceProvider = ServiceProvider()
        self.eventBus = EventBus(now=1)
        self.serviceProvider.installService(EventBus, self.eventBus)
        self.eventHandler = Test_EventBus.DummyServiceConsumer()
        self.eventHandler.setServiceProvider(self.serviceProvider)

    def test_simpleEvent(self):
        event = Test_EventBus.DummyEvent(15)
        self.assertEqual(15, event.data['test'])
        self.assertEqual('DummyEvent', repr(event))

    def test_processEvents(self):
        self.eventBus.fireEvent(Test_EventBus.DummyEvent(4))
        self.eventBus.fireEvent(Test_EventBus.DummyEvent(5))
        self.eventBus.fireEvent(Test_EventBus.DummyEvent(6))

        self.assertEqual(self.eventHandler.eventCount, 0)
        self.eventBus.processEvents()
        self.assertEqual(self.eventHandler.eventCount, 3)

    def timerHandler(self):
        self.eventBus.fireEvent(Test_EventBus.DummyEvent(6))

    def timerCallback(self):
        self.eventBus.fireEvent(Test_EventBus.DummyEvent(8))

    def test_timerEventChain(self):
        """ Tests that a timer can fire an event """
        self.eventBus.processEvents(self.eventBus.now + 2)
        self.eventBus.installTimer(1.0, handler=self.timerHandler)

        self.assertEqual(self.eventHandler.eventCount, 0)
        self.eventBus.processEvents(self.eventBus.now + 5)
        self.eventBus.processEvents(self.eventBus.now + 5)
        self.assertEqual(self.eventHandler.eventCount, 1)

    def test_timerPreempt(self):
        """ Tests that another thread can preempt a timer wait and
        force the EventBus to service events """
        self.eventBus.exec(1)
        self.eventBus.installTimer(60.0, handler=self.timerHandler)
        timer = Timer(0.1, self.timerCallback)
        timer.start()

        self.assertEqual(self.eventHandler.eventCount, 0)
        start = time()
        self.eventBus.exec(2)
        end = time()
        self.assertEqual(self.eventHandler.eventCount, 1)
        self.assertGreater(10.0, end - start)

    def test_oneShot(self):
        """ Ensure a oneShot timer fires once and can be reset """
        self.eventBus.exec(1)
        handler = self.eventBus.installTimer(
            frequency=60.0,
            handler=self.timerHandler,
            oneShot=True)

        self.eventBus.processEvents(now=self.eventBus.now + 1)
        self.assertEqual(self.eventHandler.eventCount, 0)
        self.assertTrue(handler.isQueued)
        self.eventBus.processEvents(now=self.eventBus.now + 70)
        self.eventBus.processEvents(now=self.eventBus.now)
        self.assertEqual(self.eventHandler.eventCount, 1)
        self.assertFalse(handler.isQueued)
        self.eventBus.processEvents(now=self.eventBus.now + 7000)
        self.assertEqual(self.eventHandler.eventCount, 1)
        self.assertFalse(handler.isQueued)
