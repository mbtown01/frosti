import unittest
import sys
from time import sleep

from src.power import GoGriddyEventHandler
from src.generics import PowerPriceChangedEvent
from src.events import Event, EventBus, EventHandler


class Test_GoGriddyInterface(unittest.TestCase):

    class DummyEventHandler(EventHandler):
        def __init__(self, eventBus: EventBus):
            super().__init__(eventBus)
            super()._subscribe(
                PowerPriceChangedEvent, self._powerPriceChangedEvent)

            self.__lastPrice = None

        @property
        def lastPrice(self):
            return self.__lastPrice

        def _powerPriceChangedEvent(self, event: PowerPriceChangedEvent):
            self.__lastPrice = event.price

    def setup_method(self, method):
        self.eventBus = EventBus()

        self.dummyEventHandler = \
            Test_GoGriddyInterface.DummyEventHandler(self.eventBus)
        self.goGriddyEventHandler = GoGriddyEventHandler(self.eventBus)

    def test_data(self):
        self.goGriddyEventHandler.processEvents()
        self.dummyEventHandler.processEvents()

        self.assertIsNotNone(self.dummyEventHandler.lastPrice)
