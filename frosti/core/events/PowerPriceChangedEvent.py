from frosti.core import Event


class PowerPriceChangedEvent(Event):
    """ Signals the start of a new power price in $/kW*h """
    def __init__(self, price: float, nextUpdate: float):
        super().__init__(
            name='PowerPriceChangedEvent',
            data={'price': price, 'nextUpdate': nextUpdate})

    @property
    def price(self):
        """ Current price """
        return super().data['price']

    @property
    def nextUpdate(self):
        """ Seconds between this event and next price update """
        return super().data['nextUpdate']
