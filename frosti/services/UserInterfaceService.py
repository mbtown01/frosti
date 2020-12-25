import qrcode
import smbus

from enum import Enum
from PIL import ImageFont, ImageDraw, Image
from time import sleep

from frosti.logging import log
from frosti.core import ServiceConsumer, ServiceProvider, EventBus, \
    ThermostatMode
from frosti.services.ThermostatService import ThermostatService
from frosti.services.EnvironmentSamplingService \
    import EnvironmentSamplingService
from frosti.services.OrmManagementService import OrmManagementService
from frosti.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent, SettingsChangedEvent
from frosti.core.orm import OrmGriddyUpdate


# sudo apt-get install liblcms1-dev libopenjp2-7 libtiff5 -y
# sudo apt-get install libjpeg-dev zlib1g-dev libfreetype6-dev
# pip install qrcode pillow


class UserInterfaceService(ServiceConsumer):
    """ Hardware-agnostic implemention of the FROSTI user interface, intended
    to serve as the default implementation for testing but to be subclassed
    to specialize for specific hardware
    """

    class Button(Enum):
        UP = 1
        DOWN = 2
        ENTER = 3

    def __init__(self):
        width, height = 296, 128
        self._image = Image.new('1', (width, height), 255)
        self._draw = ImageDraw.Draw(self._image)

        self._lastTemperature = None
        self._lastHumidity = None
        self._lastState = None
        self._lastPrice = None

        self._menuStructure = {
            'Mode': ['OFF', 'HEAT', 'COOL', 'FAN'],
            'Setup': None
        }

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

    @property
    def image(self):
        return self._image

    def buttonPressed(self, button):
        thermostatService = self._getService(ThermostatService)
        if UserInterfaceService.Button.ENTER == button:
            mode = thermostatService.mode
            thermostatService.nextMode()
            log.debug(f"CHANGED MODE {mode} -> {thermostatService.mode}")

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
            self.redraw()

    def _settingsChanged(self, event: SettingsChangedEvent):
        self.redraw()

    def _stateChanged(self, event: ThermostatStateChangedEvent):
        if self._lastState != event.state:
            self._lastState = event.state
            self.redraw()

    def _powerPriceChanged(self, event: PowerPriceChangedEvent):
        if self._lastPrice != event.price:
            self._lastPrice = event.price
            self.redraw()

    def redraw(self):
        # https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html
        # Draw a bounding box that I'm expecting resembles the inset for
        # the rectangle port in the case
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
        self._draw.rectangle(
            [0, 0, self._image.width, self._image.height], fill=255)

        #####################################################################
        # Draw the temperature with smaller fractional 10th in lower-right
        tempWhole, tempFrac = divmod(int(self._lastTemperature*2), 2)
        tempWholeStr, tempFracStr = str(tempWhole), f".{tempFrac*5}"
        fontWhole = ImageFont.truetype(fontName, 96)
        fontWholeMetrics = getMetrics(tempWholeStr, fontWhole)
        tempTotalHeight = fontWholeMetrics[4]-fontWholeMetrics[3]
        fontWholeLoc = (pad, int(self._image.height/2 + tempTotalHeight/2))

        fontFrac = ImageFont.truetype(fontName, 22)
        fontFracMetrics = getMetrics(tempFracStr, fontFrac)
        fontFracLoc = (fontWholeLoc[0]+fontWholeMetrics[0]-4, fontWholeLoc[1])
        tempTotalWidth = fontWholeMetrics[0] + fontFracMetrics[0] - 4

        self._draw.text(
            fontWholeLoc, tempWholeStr, fill=0, anchor='ls', font=fontWhole)
        self._draw.text(
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

        # self._draw.rectangle(fontIndoorsBox, fill=0)
        self._draw.text(
            fontIndoorsLoc, indoorsStr, fill=0, anchor='mm', font=fontIndoors)

        #####################################################################
        # Draw the current Humidity
        humidityStr = f"{int(round(self._lastHumidity))}% Humidity"
        fontHumid = ImageFont.truetype(fontName, 14)
        fontHumidMetrics = getMetrics(humidityStr, fontHumid)
        fontHumidBox = (
            (0, self._image.height -
             (fontHumidMetrics[4]-fontHumidMetrics[3]+8)),
            (tempTotalWidth, self._image.height)
        )
        fontHumidLoc = (
            int((fontHumidBox[0][0]+fontHumidBox[1][0])/2),
            int((fontHumidBox[0][1]+fontHumidBox[1][1])/2))

        self._draw.rectangle(fontHumidBox, fill=0)
        self._draw.text(
            fontHumidLoc, humidityStr, fill=255, anchor='mm', font=fontHumid)

        #####################################################################
        # Draw the current temperature target and mode
        if ThermostatMode.COOL == thermostatService.mode:
            targetStr = f"Cool to: {int(round(thermostatService.comfortMax))}"
        elif ThermostatMode.HEAT == thermostatService.mode:
            targetStr = f"Heat to: {int(round(thermostatService.comfortMin))}"
        elif ThermostatMode.AUTO == thermostatService.mode:
            targetStr = "Auto"
        elif ThermostatMode.FAN == thermostatService.mode:
            targetStr = "Fan Only"
        else:
            targetStr = 'System Off'

        fontTarget = ImageFont.truetype(fontName, 14)
        fontTargetBox = (
            (self._image.width-tempTotalWidth, 0),
            (self._image.width, fontIndoorsBox[1][1]))
        fontTargetLoc = (
            int((fontTargetBox[0][0]+fontTargetBox[1][0])/2),
            int((fontTargetBox[0][1]+fontTargetBox[1][1])/2))

        # self._draw.rectangle(fontTargetBox, fill=255, outline=0, width=1)
        self._draw.text(
            fontTargetLoc, targetStr, fill=0, anchor='mm', font=fontTarget)

        #####################################################################
        # Draw the current price
        if self._lastPrice is not None:
            priceStr = f"{self._lastPrice:.4f} $/kW*h"
            fontPrice = ImageFont.truetype(fontName, 14)
            fontPriceMetrics = getMetrics(priceStr, fontPrice)
            fontPriceBox = (
                (self._image.width-tempTotalWidth, self._image.height -
                 (fontPriceMetrics[4]-fontPriceMetrics[3]+8)),
                (self._image.width, self._image.height)
            )
            fontPriceLoc = (
                int((fontPriceBox[0][0]+fontPriceBox[1][0])/2),
                int((fontPriceBox[0][1]+fontPriceBox[1][1])/2))

            self._draw.rectangle(fontPriceBox, fill=0)
            self._draw.text(
                fontPriceLoc, priceStr, fill=255, anchor='mm', font=fontPrice)

        ormManagementService = self._getService(OrmManagementService)
        priceList = list(
            a.price for a in ormManagementService.session.query(
                OrmGriddyUpdate).order_by(OrmGriddyUpdate.time))
        if len(priceList) > 1:
            priceList.reverse()

            step = 4
            maxY = self._image.height/2 + tempTotalHeight/2
            minY = maxY-tempTotalHeight
            minX, maxX = self._image.width-tempTotalWidth, self._image.width-1
            maxSamples = int((maxX-minX+1)/step)
            priceList = priceList[:maxSamples]

            scale = 0.9*(tempTotalHeight / max(priceList))
            lineDef = list(
                (maxX-i*step, int(round(maxY-scale*p)))
                for i, p in enumerate(priceList))

            self._draw.line(
                [(minX, minY), (minX, maxY), (maxX, maxY),
                 (maxX, minY), (minX, minY)], fill=0, width=2)
            self._draw.line(lineDef, fill=0, width=1)

    def _drawQrCode(self):
        qr = qrcode.QRCode(
            version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3, border=4,
        )
        qr.add_data('http://192.168.225.16:8080/setup')
        qr.make(fit=True)
        img = qr.make_image(
            fill_color="black", back_color="white").get_image()
        self._image.paste(img, (self._image.width-img.size[0], 0))

        # epd.display(epd.getbuffer(self._image))
