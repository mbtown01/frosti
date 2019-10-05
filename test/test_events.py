import unittest
from queue import Queue
from threading import Timer
from time import time

from src.events import Event, EventBus, EventHandler
from src.generics import SensorDataChangedEvent


# class Test_EventBus(unittest.TestCase):

#     def test_put(self):
#         eventBus = EventBus()
#         queue = eventBus.subscribe()
#         event = SensorDataChangedEvent(0.0, 0.0, 0.0)
#         eventBus.fireEvent(event)

#         self.assertEqual(1, queue.qsize())
#         self.assertEqual(type(event), SensorDataChangedEvent)


class Test_EventHandler(unittest.TestCase):

    class DummyEvent(Event):
        def __init__(self, test: int):
            super().__init__('DummyEvent', {'test': test})

        @property
        def test(self):
            return super().data['test']

    class DummyEventHandler(EventHandler):
        def __init__(self, eventBus: EventBus):
            super().__init__(eventBus)
            super()._installEventHandler(
                Test_EventHandler.DummyEvent, self.__processDummyEvent)
            self.eventCount = 0

        def __processDummyEvent(self, event: Event):
            self.eventCount += 1

    def setup_method(self, method):
        self.eventBus = EventBus()
        self.eventHandler = Test_EventHandler.DummyEventHandler(self.eventBus)

    def test_simpleEvent(self):
        event = Test_EventHandler.DummyEvent(15)
        self.assertEqual(15, event.data['test'])
        self.assertEqual('DummyEvent', repr(event))

    def test_processEvents(self):
        self.eventBus.fireEvent(Test_EventHandler.DummyEvent(4))
        self.eventBus.fireEvent(Test_EventHandler.DummyEvent(5))
        self.eventBus.fireEvent(Test_EventHandler.DummyEvent(6))

        self.assertEqual(self.eventHandler.eventCount, 0)
        self.eventBus.processEvents()
        self.assertEqual(self.eventHandler.eventCount, 3)

    def timerHandler(self):
        self.eventBus.fireEvent(Test_EventHandler.DummyEvent(6))

    def timerCallback(self):
        self.eventBus.fireEvent(Test_EventHandler.DummyEvent(8))

    def test_timerEventChain(self):
        """ Tests that a timer can fire an event """
        self.eventBus.exec(1)
        self.eventBus.installTimerHandler(1.0, [self.timerHandler])

        self.assertEqual(self.eventHandler.eventCount, 0)
        self.eventBus.exec(3)
        self.assertEqual(self.eventHandler.eventCount, 1)

    def test_timerPreempt(self):
        """ Tests that another thread can preempt a timer wait and
        force the EventBus to service events """
        self.eventBus.exec(1)
        self.eventBus.installTimerHandler(60.0, [self.timerHandler])
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
        handler = self.eventBus.installTimerHandler(
            frequency=60.0,
            handlers=[self.timerHandler],
            oneShot=True)

        self.eventBus.processEvents(now=1)
        self.assertEqual(self.eventHandler.eventCount, 0)
        self.assertTrue(handler.isQueued)
        self.eventBus.processEvents(now=70)
        self.eventBus.processEvents(now=70)
        self.assertEqual(self.eventHandler.eventCount, 1)
        self.assertFalse(handler.isQueued)
        self.eventBus.processEvents(now=7000)
        self.assertEqual(self.eventHandler.eventCount, 1)
        self.assertFalse(handler.isQueued)
