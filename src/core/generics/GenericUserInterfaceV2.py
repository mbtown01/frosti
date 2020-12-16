from enum import Enum
from PIL import ImageFont, ImageDraw, Image
import qrcode

from src.core import ServiceConsumer, ServiceProvider, EventBus, Event
from src.services import ThermostatService
from src.core.events import ThermostatStateChangedEvent, \
    SensorDataChangedEvent, PowerPriceChangedEvent, \
    SettingsChangedEvent


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

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        eventBus = self._getService(EventBus)

        eventBus.installEventHandler(
            SettingsChangedEvent, self.__settingsChanged)
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

    def __settingsChanged(self, event: SettingsChangedEvent):
        pass

    def __stateChanged(self, event: ThermostatStateChangedEvent):
        self.redraw()

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        self.redraw()

    @property
    def image(self):
        return self._image

    def redraw(self):

        def get_text_dimensions(text_string, font):
            # https://stackoverflow.com/a/46220683/9263761
            ascent, descent = font.getmetrics()

            text_width = font.getmask(text_string).getbbox()[2]
            text_height = font.getmask(text_string).getbbox()[3]

            return (text_width, text_height, ascent-text_height)

        temperature = '72'
        font = ImageFont.truetype("segoe-ui.ttf", 72)
        size = get_text_dimensions(temperature, font)
        fontLoc = (8, self._image.height/2 - size[1]/2)
        self._draw.rectangle([8, 8, 296-8, 128-8], fill=0)
        self._draw.rectangle([9, 9, 296-9, 128-9], fill=255)
        self._draw.rectangle(
            [fontLoc[0], fontLoc[1],
             fontLoc[0]+size[0], fontLoc[1]+size[1]], fill=0)
        self._draw.rectangle(
            [fontLoc[0]+1, fontLoc[1]+1,
             fontLoc[0]+size[0]-1, fontLoc[1]+size[1]-1], fill=255)

        fontLoc = (fontLoc[0], fontLoc[1]-size[2])
        self._draw.text(fontLoc, temperature, fill=0, font=font)

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
