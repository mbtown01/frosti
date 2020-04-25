import requests
import json
from threading import Thread

from .ConfigService import ConfigService
from src.core import EventBusMember, ServiceProvider
from src.core.events import PowerPriceChangedEvent
from src.logging import log

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


class GoGriddyPriceCheckService(EventBusMember):
    """ EventBusMember thread that monitors power prices and fires an event
    if there is a change """

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(ConfigService)
        self.__apiUrl = config.resolve('gogriddy', 'apiUrl')
        self.__apiPostData = {
            'meterID': config.resolve('gogriddy', 'meterId'),
            'memberID': config.resolve('gogriddy', 'memberId'),
            'settlement_point': config.resolve('gogriddy', 'settlementPoint')
        }
        self.__startUpdatePriceHandler = \
            super()._installTimerHandler(
                5.0, self.__startUpdatePrice, oneShot=True)

    def __startUpdatePrice(self):
        """ Kickoff a 2nd thread to get the actual power price """
        Thread(target=self.__updatePrice, name="GoGriddy updater").start()

    def __updatePrice(self):
        """ Gets the current price info and fires a PowerPriceChangedEvent.
        Designed to be called on another thread to not block execution """
        result = requests.post(
            self.__apiUrl, data=json.dumps(self.__apiPostData))
        data = json.loads(result.text)
        event = PowerPriceChangedEvent(
            price=float(data["now"]["price_ckwh"]) / 100.0,
            nextUpdate=float(data['seconds_until_refresh'])
        )

        self.__startUpdatePriceHandler.reset(frequency=event.nextUpdate)
        log.info(
            f"Power price is now {event.price:.4f}/kW*h, next update "
            f"in {event.nextUpdate}s")

        self._fireEvent(event)
