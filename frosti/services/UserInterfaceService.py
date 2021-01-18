from frosti.core.orm import OrmGriddyUpdate
from frosti.core.Event import Event
import qrcode
import smbus

from enum import Enum
from PIL import ImageFont, ImageDraw, Image
from time import sleep
from datetime import datetime, timedelta

from frosti.logging import log
from frosti.core import ServiceConsumer, ServiceProvider, EventBus, \
    ThermostatMode
from frosti.services.ThermostatService import ThermostatService
from frosti.services.EnvironmentSamplingService \
    import EnvironmentSamplingService
from frosti.services.OrmManagementService import OrmManagementService
from frosti.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent, SettingsChangedEvent
from frosti.core.Event import Event


# sudo apt-get install liblcms1-dev libopenjp2-7 libtiff5 -y
# sudo apt-get install libjpeg-dev zlib1g-dev libfreetype6-dev
# pip install qrcode pillow


class HardwareButton(Enum):
    UP = 1
    DOWN = 2
    ENTER = 3


class ScreenInvalidatedEvent(Event):
    def __init__(self, screen):
        super().__init__(data={
            'screen': screen,
        })

    @property
    def screen(self):
        return self._data['screen']


class Screen(ServiceConsumer):

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.isActive = False

    def buttonPressed(self, button: HardwareButton):
        raise NotImplementedError()

    def redraw(self, draw: ImageDraw.Draw):
        raise NotImplementedError()

    def invalidate(self):
        if self.isActive:
            eventBus = self._getService(EventBus)
            eventBus.fireEvent(
                ScreenInvalidatedEvent(self), immediately=True)


class OptionsScreen(Screen):

    def __init__(self, width, height):
        super().__init__(width, height)

        self._lastTemperature = None
        self._lastHumidity = None
        self._lastState = None
        self._lastPrice = None

        self._options = ['Mode', 'Settings', 'Network', 'Reset']
        self._selectedIndex = 0

    def buttonPressed(self, button: HardwareButton):
        if HardwareButton.ENTER == button:
            self.invalidate()
        elif HardwareButton.UP == button:
            self._selectedIndex = \
                (self._selectedIndex - 1) % len(self._options)
            self.invalidate()
        elif HardwareButton.DOWN == button:
            self._selectedIndex = \
                (self._selectedIndex + 1) % len(self._options)
            self.invalidate()
        else:
            raise RuntimeError(f"Unknown button: {button}")

    def redraw(self, draw: ImageDraw.Draw):

        def getMetrics(text, font):
            ascent, descent = font.getmetrics()
            (width, baseline), (offset_x, offset_y) = \
                font.font.getsize(str(text))
            return (width, baseline, offset_x, offset_y, ascent, descent)

        # fontName = 'Hack-Bold.ttf'
        # font = ImageFont.truetype(fontName, 16)
        # fontMetrics = getMetrics('Arugula', font)
        # for i, text in enumerate(self._options):
        #     fontIndoorsBox = (
        #         (0, 0),
        #         (tempTotalWidth, fontMetrics[4]-fontMetrics[3]+8)
        #     )
        #     fontIndoorsLoc = (
        #         int((fontMetrics[0][0]+fontMetrics[1][0])/2),
        #         int((fontMetrics[0][1]+fontMetrics[1][1])/2))

        #     # self.draw.rectangle(fontIndoorsBox, fill=0)
        #     self.draw.text(
        #         fontIndoorsLoc, indoorsStr, fill=0, anchor='mm', font=fontIndoors)


class HomeScreen(Screen):
    """ Hardware-agnostic implemention of the FROSTI user interface, intended
    to serve as the default implementation for testing but to be subclassed
    to specialize for specific hardware
    """

    def __init__(self, width, height):
        super().__init__(width, height)

        self._lastTemperature = None
        self._lastHumidity = None
        self._lastState = None
        self._lastPrice = None

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        environmentSamplingService = \
            self._getService(EnvironmentSamplingService)
        self._lastTemperature = environmentSamplingService.temperature
        self._lastHumidity = environmentSamplingService.humidity

        eventBus = self._getService(EventBus)
        eventBus.installEventHandler(
            SensorDataChangedEvent, self._sensorDataChanged)
        eventBus.installEventHandler(
            ThermostatStateChangedEvent, self._stateChanged)
        eventBus.installEventHandler(
            PowerPriceChangedEvent, self._powerPriceChanged)
        eventBus.installEventHandler(
            SettingsChangedEvent, self._settingsChanged)

    def buttonPressed(self, button: HardwareButton):
        thermostatService = self._getService(ThermostatService)
        if HardwareButton.ENTER == button:
            mode = thermostatService.mode
            thermostatService.nextMode()
            log.debug(f"CHANGED MODE {mode} -> {thermostatService.mode}")
        elif HardwareButton.UP == button:
            thermostatService.modifyComfortSettings(1)
        elif HardwareButton.DOWN == button:
            thermostatService.modifyComfortSettings(-1)
        else:
            raise RuntimeError(f"Unknown button: {button}")

    def _sensorDataChanged(self, event: SensorDataChangedEvent):
        needsRedraw = False

        if abs(self._lastTemperature-event.temperature) > 0.25:
            log.debug(f"Temperature changed {self._lastTemperature} "
                      f"-> {event.temperature}")
            self._lastTemperature = event.temperature
            needsRedraw = True

        if abs(self._lastHumidity-event.humidity) > 0.5:
            log.debug(f"Humidity changed {self._lastHumidity} "
                      f"-> {event.humidity}")
            self._lastHumidity = event.humidity
            needsRedraw = True

        if needsRedraw:
            self.invalidate()

    def _settingsChanged(self, event: SettingsChangedEvent):
        self.invalidate()

    def _stateChanged(self, event: ThermostatStateChangedEvent):
        if self._lastState != event.state:
            self._lastState = event.state
            self.invalidate()

    def _powerPriceChanged(self, event: PowerPriceChangedEvent):
        if self._lastPrice != event.price:
            self._lastPrice = event.price
            self.invalidate()

    def redraw(self, draw: ImageDraw.Draw):
        # https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
        # Draw a bounding box that I'm expecting resembles the inset for
        # the rectangle port in the case
        #
        # NOTE that I had a heck of a time getting the align='*' features to
        # work until I forced the RPi to upgrade Pillow, which seems to
        # default to v5.x but v8.x works for me
        pad = 2
        fontName = 'Hack-Bold.ttf'
        thermostatService = self._getService(ThermostatService)

        def getMetrics(text, font):
            ascent, descent = font.getmetrics()
            (width, baseline), (offset_x, offset_y) = \
                font.font.getsize(str(text))
            return (width, baseline, offset_x, offset_y, ascent, descent)

        #####################################################################
        # Clear the image
        draw.rectangle(
            [0, 0, self.width, self.height], fill=255)

        #####################################################################
        # Draw the temperature with smaller fractional 10th in lower-right
        tempWhole, tempFrac = divmod(int(self._lastTemperature*2), 2)
        tempWholeStr, tempFracStr = str(tempWhole), f".{tempFrac*5}"
        fontWhole = ImageFont.truetype(fontName, 96)
        fontWholeMetrics = getMetrics(tempWholeStr, fontWhole)
        tempTotalHeight = fontWholeMetrics[4]-fontWholeMetrics[3]
        fontWholeLoc = (pad, int(self.height/2 + tempTotalHeight/2))

        fontFrac = ImageFont.truetype(fontName, 22)
        fontFracMetrics = getMetrics(tempFracStr, fontFrac)
        fontFracLoc = (fontWholeLoc[0]+fontWholeMetrics[0]-4, fontWholeLoc[1])
        tempTotalWidth = fontWholeMetrics[0] + fontFracMetrics[0] - 4

        draw.text(
            fontWholeLoc, tempWholeStr, fill=0, anchor='ls', font=fontWhole)
        draw.text(
            fontFracLoc, tempFracStr, fill=0, anchor='ls', font=fontFrac)

        #####################################################################
        # Draw the 'Indoors' logo above the temperature
        indoorsStr = 'Indoors'
        fontIndoors = ImageFont.truetype(fontName, 14)
        fontIndoorsMetrics = getMetrics(indoorsStr, fontIndoors)
        fontIndoorsBox = (
            (0, 0),
            (tempTotalWidth, fontIndoorsMetrics[4]-fontIndoorsMetrics[3]+8)
        )
        fontIndoorsLoc = (
            int((fontIndoorsBox[0][0]+fontIndoorsBox[1][0])/2),
            int((fontIndoorsBox[0][1]+fontIndoorsBox[1][1])/2))

        # draw.rectangle(fontIndoorsBox, fill=0)
        draw.text(
            fontIndoorsLoc, indoorsStr, fill=0, anchor='mm', font=fontIndoors)

        #####################################################################
        # Draw the current Humidity
        humidityStr = f"{int(round(self._lastHumidity))}% Humidity"
        fontHumid = ImageFont.truetype(fontName, 14)
        fontHumidMetrics = getMetrics(humidityStr, fontHumid)
        fontHumidBox = (
            (0, self.height -
             (fontHumidMetrics[4]-fontHumidMetrics[3]+8)),
            (tempTotalWidth, self.height)
        )
        fontHumidLoc = (
            int((fontHumidBox[0][0]+fontHumidBox[1][0])/2),
            int((fontHumidBox[0][1]+fontHumidBox[1][1])/2))

        draw.rectangle(fontHumidBox, fill=0)
        draw.text(
            fontHumidLoc, humidityStr, fill=255, anchor='mm', font=fontHumid)

        #####################################################################
        # Draw the current temperature target and mode
        comfortMin = int(round(thermostatService.comfortMin))
        comfortMax = int(round(thermostatService.comfortMax))

        if ThermostatMode.COOL == thermostatService.mode:
            targetStr = f"Cool to: {comfortMax}"
        elif ThermostatMode.HEAT == thermostatService.mode:
            targetStr = f"Heat to: {comfortMin}"
        elif ThermostatMode.AUTO == thermostatService.mode:
            targetStr = f"Auto: {comfortMin} / {comfortMax}"
        elif ThermostatMode.FAN == thermostatService.mode:
            targetStr = "Fan Only"
        else:
            targetStr = 'System Off'

        fontTarget = ImageFont.truetype(fontName, 14)
        fontTargetBox = (
            (self.width-tempTotalWidth, 0),
            (self.width, fontIndoorsBox[1][1]))
        fontTargetLoc = (
            int((fontTargetBox[0][0]+fontTargetBox[1][0])/2),
            int((fontTargetBox[0][1]+fontTargetBox[1][1])/2))

        # draw.rectangle(fontTargetBox, fill=255, outline=0, width=1)
        draw.text(
            fontTargetLoc, targetStr, fill=0, anchor='mm', font=fontTarget)

        #####################################################################
        # Draw the current price
        if self._lastPrice is not None:
            priceStr = f"${self._lastPrice:.4f}/kW*h"
            fontPrice = ImageFont.truetype(fontName, 14)
            fontPriceMetrics = getMetrics(priceStr, fontPrice)
            fontPriceBox = (
                (self.width-tempTotalWidth, self.height -
                 (fontPriceMetrics[4]-fontPriceMetrics[3]+8)),
                (self.width, self.height)
            )
            fontPriceLoc = (
                int((fontPriceBox[0][0]+fontPriceBox[1][0])/2),
                int((fontPriceBox[0][1]+fontPriceBox[1][1])/2))

            draw.rectangle(fontPriceBox, fill=0)
            draw.text(
                fontPriceLoc, priceStr, fill=255, anchor='mm', font=fontPrice)

        #####################################################################
        # Draw the price trend
        ormManagementService = self._getService(OrmManagementService)
        minutesInChart = 6*60
        minutesInSample = 15
        now = datetime.now().astimezone()
        earliestTime = now - timedelta(minutes=minutesInChart)

        vPad = 8
        maxY = self.height/2 + tempTotalHeight/2
        minY = maxY-tempTotalHeight
        minX, maxX = self.width-tempTotalWidth, self.width-1
        draw.rectangle(
            [minX, minY, maxX, maxY], outline=0, fill=255, width=3)
        minX, maxX = minX+2, maxX-2

        priceList = list(
            (a.time, a.price) for a in ormManagementService.session
            .query(OrmGriddyUpdate).order_by(OrmGriddyUpdate.time)
            .filter(OrmGriddyUpdate.time > earliestTime)
            .filter(OrmGriddyUpdate.time <= now))
        if len(priceList):
            totalSamples = minutesInChart // minutesInSample
            priceRangeList = [(None, None)] * totalSamples
            for time, price in priceList:
                timeSpan = now.timestamp() - time.timestamp()
                timeBin = int(timeSpan // (minutesInSample*60))
                minPrice, maxPrice = priceRangeList[timeBin]
                minPrice = price if minPrice is None else minPrice
                minPrice = min(minPrice, price)
                maxPrice = price if maxPrice is None else maxPrice
                maxPrice = max(maxPrice, price)
                priceRangeList[timeBin] = (minPrice, maxPrice)

            absMinPrice = min(a[0] for a in priceRangeList if a[0] is not None)
            absMinPrice = min(0, absMinPrice)
            absMaxPrice = max(a[1] for a in priceRangeList if a[1] is not None)
            absMinPriceAdj = absMinPrice + 0.05*(absMaxPrice-absMinPrice)
            absMaxPriceAdj = absMaxPrice + 0.05*(absMaxPrice-absMinPrice)
            scale = ((tempTotalHeight-vPad) / (absMaxPriceAdj-absMinPriceAdj))

            def priceToY(price: float):
                return int(round(maxY-(price-absMinPriceAdj)*scale)) - vPad/2

            if absMinPrice < 0.0:
                draw.line([minX, priceToY(0), maxX, priceToY(0)], fill=0)

            priceWidth = (maxX-minX) / totalSamples
            for i, (minPrice, maxPrice) in enumerate(priceRangeList):
                if minPrice is not None and maxPrice is not None:
                    draw.rectangle(
                        [maxX - int((i+1)*priceWidth), priceToY(minPrice),
                         maxX - int(i*priceWidth), priceToY(maxPrice)],
                        fill=0, width=1)


class UserInterfaceService(ServiceConsumer):
    """ Hardware-agnostic implemention of the FROSTI user interface, intended
    to serve as the default implementation for testing but to be subclassed
    to specialize for specific hardware
    """

    def __init__(self, width, height):
        self.image = Image.new('1', (width, height), 255)
        self.draw = ImageDraw.Draw(self.image)

        self._lastTemperature = None
        self._lastHumidity = None
        self._lastState = None
        self._lastPrice = None
        self._currentScreen = HomeScreen(width, height)
        self._currentScreen.isActive = True

        # Stuff the user needs to do
        # Change MODE
        # See current program information
        # See network configuration
        # Change defaults

        # BACK...
        # MODE
        # SETTINGS
        # STATUS
        # CONFIG

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)
        self._currentScreen.setServiceProvider(provider)

        eventBus = self._getService(EventBus)
        eventBus.installEventHandler(
            ScreenInvalidatedEvent, self._screenInvalidated)

    def _screenInvalidated(self, event: ScreenInvalidatedEvent):
        self.redraw()

    def buttonPressed(self, button: HardwareButton):
        self._currentScreen.buttonPressed(button)

    def redraw(self):
        self._currentScreen.redraw(self.draw)

    def _drawQrCode(self):
        qr = qrcode.QRCode(
            version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3, border=4,
        )
        qr.add_data('http://192.168.225.16:8080/setup')
        qr.make(fit=True)
        img = qr.make_image(
            fill_color="black", back_color="white").get_image()
        self.image.paste(img, (self.image.width-img.size[0], 0))

        # epd.display(epd.getbuffer(self.image))
