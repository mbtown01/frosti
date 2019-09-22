import requests
import json
import sys
from datetime import datetime

from src.events import Event, EventHandler, EventBus
from src.config import config
from src.generics import PowerPriceChangedEvent
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


class GoGriddyEventHandler(EventHandler):
    """ EventHandler thread that monitors power prices and fires an event
    if there is a change """

    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus, loopSleep=5.0)

        self.__apiPostData = {
            'meterID': config.gogriddy_meterId,
            'memberID': config.gogriddy_meterId,
            'settlement_point': config.gogriddy_settlementPoint
        }
        self.__nextPoll = datetime.now().timestamp()-1
        self.__rawData = None
        self.__updatePrice()

    def __updatePrice(self):
        """ Returns the new power price in $/kW*h """
        timeStamp = datetime.now().timestamp()
        if self.__rawData is None or self.__nextPoll <= timeStamp:
            result = requests.post(
                config.gogriddy_apiUrl, data=json.dumps(self.__apiPostData))
            self.__rawData = json.loads(result.text)
            self.__nextPoll = \
                timeStamp + float(self.__rawData['seconds_until_refresh'])
            price = float(self.__rawData["now"]["price_ckwh"])/100.0
            self._fireEvent(PowerPriceChangedEvent(price))

            log.info(f"GoGriddy power price is now {price:.4f}/kW*h")

    def processEvents(self):
        """ Poll the price prover and figre an event if price changed """
        super().processEvents()

        self.__updatePrice()
