import requests
import json
from threading import Thread

from .OrmManagementService import OrmManagementService
from frosti.core import ServiceConsumer, ServiceProvider, EventBus
from frosti.core.events import PowerPriceChangedEvent
from frosti.logging import log, handleException

API_URL = 'https://app.gogriddy.com/api/v1/insights/getnow'

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


class GoGriddyPriceCheckService(ServiceConsumer):
    """ ServiceConsumer thread that monitors power prices and fires an event
    if there is a change """

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        ormManagementService = self._getService(OrmManagementService)
        self.__apiPostData = dict()
        self.__apiPostData['meterID'] = \
            ormManagementService.getConfigString('gogriddy.meterId', '')
        self.__apiPostData['memberID'] = \
            ormManagementService.getConfigString('gogriddy.memberId', '')
        self.__apiPostData['settlement_point'] = \
            ormManagementService.getConfigString(
                'gogriddy.settlementPoint', '')

        # Only start the price check service if a member id has been
        # configured
        if \
                self.__apiPostData['meterID'] != '' and \
                self.__apiPostData['memberID'] != '' and \
                self.__apiPostData['settlement_point'] != '':
            eventBus = self._getService(EventBus)
            self.__startUpdatePriceHandler = eventBus.installTimer(
                5.0, handler=self.__startUpdatePrice, oneShot=True)

    def __startUpdatePrice(self):
        """ Kickoff a 2nd thread to get the actual power price """
        Thread(target=self.__updatePrice, name="GoGriddy updater").start()

    def __updatePrice(self):
        """ Gets the current price info and fires a PowerPriceChangedEvent.
        Designed to be called on another thread to not block execution """
        eventBus = self._getService(EventBus)

        try:
            result = requests.post(
                API_URL, data=json.dumps(self.__apiPostData))
            data = json.loads(result.text)
            event = PowerPriceChangedEvent(
                price=float(data["now"]["price_ckwh"]) / 100.0,
                nextUpdate=float(data['seconds_until_refresh'])
            )

            self.__startUpdatePriceHandler.reset(frequency=event.nextUpdate)
            log.info(
                f"Power price is now {event.price:.4f}/kW*h, next update "
                f"in {event.nextUpdate}s")

            eventBus.fireEvent(event)
        except:
            handleException(
                "GoGriddy price checker, retrying in 60s")
            self.__startUpdatePriceHandler.reset(frequency=60)
