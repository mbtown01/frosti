import unittest
from time import strptime, mktime

from frosti.services import GoGriddyPriceCheckService
from frosti.core.events import PowerPriceChangedEvent
from frosti.core import EventBus, ServiceConsumer, ServiceProvider


class Test_GoGriddyInterface(unittest.TestCase):

    class DummyServiceConsumer(ServiceConsumer):
        def __init__(self):
            self.lastPrice = None
            self.netUpdate = None

        def setServiceProvider(self, provider: ServiceProvider):
            eventBus = self._getService(EventBus)
            eventBus.installEventHandler(
                PowerPriceChangedEvent, self._powerPriceChangedEvent)

        def _powerPriceChangedEvent(self, event: PowerPriceChangedEvent):
            self.lastPrice = event.price
            self.nextUpdate = event.nextUpdate

    def setup_method(self, method):
        self.serviceProvider = ServiceProvider()
        testTime = strptime('01/01/19 08:01:00', '%m/%d/%y %H:%M:%S')
        self.eventBus = EventBus(now=mktime(testTime))
        self.serviceProvider.installService(EventBus, self.eventBus)

        self.dummyEventBusMember = \
            Test_GoGriddyInterface.DummyServiceConsumer()
        self.dummyEventBusMember.setServiceProvider(self.serviceProvider)
        self.priceChecker = GoGriddyPriceCheckService()
        self.priceChecker.setServiceProvider(self.serviceProvider)

    # def test_data(self):
    #     self.eventBus.exec(2)

    #     self.assertIsNotNone(self.dummyEventBusMember.nextUpdate)
    #     self.assertIsNotNone(self.dummyEventBusMember.lastPrice)
