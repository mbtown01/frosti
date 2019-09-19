import requests
import json
import sys

from src.events import Event, EventHandler, EventBus
from src.config import config

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


class PowerRateChangedEvent(Event):
    """ Signals the start of a new power rate """

    def __init__(self, rate: float):
        super().__init__(data={'rate': rate})

    @property
    def rate(self):
        return self._data['rate']


class GoGriddyPowerInterface:

    def __init__(self):
        self.__apiPostData = {
            'meterID': config.gogriddy_meterId,
            'memberID': config.gogriddy_meterId,
            'settlement_point': config.gogriddy_settlementPoint
        }

    def getRawData(self):
        result = requests.post(
            config.gogriddy_apiUrl, data=json.dumps(self.__apiPostData))

        return json.loads(result.text)

    def getCurrentRate(self):
        data = self.getRawData()

        # 'seconds_until_refresh'

        return float(data["now"]["price_ckwh"])/100.0

    def getForecast(self):
        data = self.getRawData()

        for pair in data["forecast"]:
            print(pair)

        # 'date_local_tz'
        # 'price_ckwh'

        return None


class GoGriddyPowerEventHandler(EventHandler):

    def __init__(self, eventBus: EventBus, loopSleep: int):
        super().__init__(eventBus, loopSleep)
