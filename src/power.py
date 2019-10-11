import requests
import json
import sys
from time import time
from threading import Thread

from src.events import Event, EventHandler, EventBus
from src.config import config
from src.generics import PowerPriceChangedEvent
from src.logging import log
from src.services import ServiceProvider

# GoGriddy billing is actually based on 15-minute RTSPP intervals indicated
# here
# http://www.ercot.com/content/cdr/html/20190915_real_time_spp
#
# Billing explained
# https://www.gogriddy.com/wp-content/themes/griddy/assets/downloads/Electricity-Facts-Label.pdf
#
# Current grid rate from ERCOT
# http://www.ercot.com/content/cdr/html/rtd_ind_lmp_lz_hb_LZ_HOUSTON.html
#
# Since billed on the quarter-hour, if a price spike happens it's likely
# smart to ride until the next window before consuming power again before
# consuming power again


class GoGriddyEventHandler(EventHandler):
    """ EventHandler thread that monitors power prices and fires an event
    if there is a change """

    def __init__(self):
        self.__apiUrl = config.resolve('gogriddy', 'apiUrl')
        self.__apiPostData = {
            'meterID': config.resolve('gogriddy', 'meterId'),
            'memberID': config.resolve('gogriddy', 'memberId'),
            'settlement_point': config.resolve('gogriddy', 'settlementPoint')
        }

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)
        super()._installEventHandler(
            type(PowerPriceChangedEvent), self.__powerPriceChanged)
        self.__startUpdatePriceHandler = \
            super()._installTimerHandler(300.0, self.__startUpdatePrice)

        self.__startUpdatePrice()

    def __startUpdatePrice(self):
        Thread(target=self.__updatePrice, name="GoGriddy updater").start()

    def __updatePrice(self, wait: float=0):
        """ Gets the current price info and fires a PowerPriceChangedEvent.
        Designed to be called on another thread to not block execution """
        result = requests.post(
            self.__apiUrl, data=json.dumps(self.__apiPostData))
        data = json.loads(result.text)

        self._fireEvent(PowerPriceChangedEvent(
            price=float(data["now"]["price_ckwh"])/100.0,
            nextUpdate=float(data['seconds_until_refresh'])
        ))

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        log.info(f"GoGriddy power price is now {event.price:.4f}/kW*h")
        self.__startUpdatePriceHandler.reset(frequency=event.nextUpdate)
