import unittest
import sys
from time import strptime, mktime

from src.services import GoGriddyPriceCheckService
from src.core.events import PowerPriceChangedEvent
from src.core import Event, EventBus, EventBusMember, ServiceProvider
from src.settings import Settings


class Test_GoGriddyInterface(unittest.TestCase):

    class DummyEventBusMember(EventBusMember):
        def __init__(self):
            self.lastPrice = None
            self.netUpdate = None

        def setServiceProvider(self, provider: ServiceProvider):
            super()._installEventHandler(
                PowerPriceChangedEvent, self._powerPriceChangedEvent)

        def _powerPriceChangedEvent(self, event: PowerPriceChangedEvent):
            self.lastPrice = event.price
            self.nextUpdate = event.nextUpdate

    def setup_method(self, method):
        self.serviceProvider = ServiceProvider()
        testTime = strptime('01/01/19 08:01:00', '%m/%d/%y %H:%M:%S')
        self.eventBus = EventBus(now=mktime(testTime))
        self.serviceProvider.installService(EventBus, self.eventBus)
        self.settings = Settings()
        self.settings.setServiceProvider(self.serviceProvider)
        self.serviceProvider.installService(Settings, self.settings)

        self.dummyEventBusMember = \
            Test_GoGriddyInterface.DummyEventBusMember()
        self.dummyEventBusMember.setServiceProvider(self.serviceProvider)
        self.priceChecker = GoGriddyPriceCheckService()
        self.priceChecker.setServiceProvider(self.serviceProvider)

    # def test_data(self):
    #     self.eventBus.exec(2)

    #     self.assertIsNotNone(self.dummyEventBusMember.nextUpdate)
    #     self.assertIsNotNone(self.dummyEventBusMember.lastPrice)
