from enum import Enum
from PIL import ImageFont, ImageDraw, Image
import qrcode

from src.core import ServiceConsumer, ServiceProvider, EventBus, Event
from src.services.ThermostatService import ThermostatService
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent


class GenericUserInterfaceV2(ServiceConsumer):
    """ Hardware-agnostic implemention of the FROSTI user interface
    """

    class Button(Enum):
        UP = 1
        DOWN = 2
        ENTER = 3

    class ButtonPressedEvent(Event):
        def __init__(self, button):
            super().__init__(data={'button': button})

        @property
        def button(self):
            return super().data['button']

    def __init__(self):
        width, height = 296, 128
        self._image = Image.new('1', (width, height), 255)
        self._draw = ImageDraw.Draw(self._image)

        self._lastState = 'NONE'

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        eventBus = self._getService(EventBus)

        eventBus.installEventHandler(
            SensorDataChangedEvent, self.__sensorDataChanged)
        eventBus.installEventHandler(
            ThermostatStateChangedEvent, self.__stateChanged)
        eventBus.installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)
        eventBus.installEventHandler(
            GenericUserInterfaceV2.ButtonPressedEvent,
            self.__buttonPressedHandler)

    def __sensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.redraw()

    def __buttonPressedHandler(self, event: ButtonPressedEvent):
        thermostatService = self._getService(ThermostatService)
        self.backlightReset()

        if event.button == GenericUserInterfaceV2.Button.UP:
            thermostatService.modifyComfortSettings(1)
        elif event.button == GenericUserInterfaceV2.Button.DOWN:
            thermostatService.modifyComfortSettings(-1)
        elif event.button == GenericUserInterfaceV2.Button.ENTER:
            pass

    def __stateChanged(self, event: ThermostatStateChangedEvent):
        self.redraw()

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        self.redraw()

    @property
    def image(self):
        return self._image

    def drawCurrentTemp(self, temperature: float):
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

        # Draw the temperature with smaller fractional 10th in lower-right
        tempWhole, tempFrac = divmod(int(temperature*10), 10)
        fontWhole = ImageFont.truetype(fontName, 82)
        fontWholeMetrics = getMetrics(str(tempWhole), fontWhole)
        fontWholeLoc = (
            pad, self._image.height/2 +
            (fontWholeMetrics[4]-fontWholeMetrics[3])/2)

        fontFrac = ImageFont.truetype(fontName, 22)
        fontFracMetrics = getMetrics(f".{tempFrac}", fontFrac)
        fontFracLoc = (fontWholeLoc[0]+fontWholeMetrics[0]-4, fontWholeLoc[1])

        self._draw.text(
            fontWholeLoc, str(tempWhole), fill=0, anchor='ls', font=fontWhole)
        self._draw.text(
            fontFracLoc, f".{tempFrac}", fill=0, anchor='ls', font=fontFrac)

        # Draw the current state
        stateStr = str(thermostatService.state)
        fontState = ImageFont.truetype(fontName, 16)
        fontStateMetrics = getMetrics(stateStr, fontState)
        fontStateBox = (
            (0, 0),
            (fontWholeMetrics[0] + fontFracMetrics[0] - 4,
             fontStateMetrics[4]-fontStateMetrics[3]+8)
        )
        fontStateLoc = (
            (fontStateBox[0][0]+fontStateBox[1][0])/2,
            (fontStateBox[0][1]+fontStateBox[1][1])/2)

        self._draw.rectangle(fontStateBox, fill=0)
        self._draw.text(
            fontStateLoc, stateStr, fill=255, anchor='mm', font=fontState)

        # Draw the temperature target
        targetStr = 'Target: 72'
        fontTarget = ImageFont.truetype(fontName, 16)
        fontTargetMetrics = getMetrics(targetStr, fontTarget)
        fontTargetBox = (
            (0, self._image.height -
             (fontTargetMetrics[4]-fontTargetMetrics[3]+8)),
            (fontWholeMetrics[0] + fontFracMetrics[0] - 4,
             self._image.height)
        )
        fontTargetLoc = (
            (fontTargetBox[0][0]+fontTargetBox[1][0])/2,
            (fontTargetBox[0][1]+fontTargetBox[1][1])/2)

        self._draw.rectangle(fontTargetBox, fill=0)
        self._draw.text(
            fontTargetLoc, targetStr, fill=255, anchor='mm', font=fontTarget)

    def drawQrCode(self):
        qr = qrcode.QRCode(
            version=1, error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3, border=4,
        )
        qr.add_data('http://192.168.225.16:8080/setup')
        qr.make(fit=True)
        img = qr.make_image(
            fill_color="black", back_color="white").get_image()
        self._image.paste(img, (self._image.width-img.size[0], 0))

    def redraw(self):
        self.drawCurrentTemp(72.5)

        # epd.display(epd.getbuffer(self._image))
