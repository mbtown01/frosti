import unittest
import sys

from src.power import GoGriddyEventHandler
from src.generics import PowerPriceChangedEvent
from src.events import Event, EventBus, EventHandler


class Test_GoGriddyInterface(unittest.TestCase):

    class DummyEventHandler(EventHandler):
        def __init__(self, eventBus: EventBus):
            super().__init__(eventBus)
            super()._installEventHandler(
                PowerPriceChangedEvent, self._powerPriceChangedEvent)

            self.lastPrice = None
            self.netUpdate = None

        def _powerPriceChangedEvent(self, event: PowerPriceChangedEvent):
            self.lastPrice = event.price
            self.nextUpdate = event.nextUpdate

    def setup_method(self, method):
        self.eventBus = EventBus()

        self.dummyEventHandler = \
            Test_GoGriddyInterface.DummyEventHandler(self.eventBus)
        self.goGriddyEventHandler = GoGriddyEventHandler(self.eventBus)

    def test_data(self):
        self.eventBus.exec(2)

        self.assertIsNotNone(self.dummyEventHandler.nextUpdate)
        self.assertIsNotNone(self.dummyEventHandler.lastPrice)
