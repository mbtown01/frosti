from time import sleep, strftime
from PIL import ImageChops, Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO

from frosti.services.UserInterfaceService \
    import UserInterfaceService as BaseUserInterfaceService
from frosti.core import ServiceProvider, EventBus
from frosti.hardware.epd2in9 import EPD
from frosti.logging import log


class UserInterfaceService(BaseUserInterfaceService):

    def __init__(self):
        super().__init__()

        self._epd = EPD()
        self._epd.init(self._epd.lut_partial_update)
        self._epd.Clear(0xFF)
        self._epd.Clear(0x00)
        self._epd.Clear(0xFF)
        # font24 = ImageFont.truetype('Hack-Bold.ttf', 24)

        # time_image = Image.new('1', (self._epd.height, self._epd.width), 255)
        # time_draw = ImageDraw.Draw(time_image)
        # while (True):
        #     time_str = strftime('%H:%M:%S')
        #     time_draw.rectangle((10, 10, 120, 50), fill=255)
        #     time_draw.text((10, 10), time_str, font=font24, fill=0)
        #     # newimage = time_image.crop([10, 10, 120, 50])
        #     # time_image.paste(newimage, (10, 10))
        #     bbox = (10, 10, 120, 50)
        #     x1 = bbox[1]
        #     y1 = self._epd.width - bbox[2] - 1
        #     x2 = bbox[2]
        #     y2 = self._epd.width - bbox[0] - 1
        #     self._epd.displayWin(
        #         x1, y1, x2, y2, self._epd.getbuffer(time_image))
        #     # self._epd.display(self._epd.getbuffer(time_image))
        #     log.debug(f"Drawing {time_str}")

        # logging.info("Clear...")
        # self._epd.init(self._epd.lut_full_update)
        # self._epd.Clear(0xFF)

        # logging.info("Goto Sleep...")
        # self._epd.sleep()
        # self._epd.Dev_exit()

        self._buttonMap = {
            23: BaseUserInterfaceService.Button.UP,
            27: BaseUserInterfaceService.Button.ENTER,
            22: BaseUserInterfaceService.Button.DOWN,
        }

        for pin in self._buttonMap.keys():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(
                pin, GPIO.FALLING,
                callback=self._buttonPressHandler, bouncetime=25)

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)
        self.__eventBus = self._getService(EventBus)

        self._epaperTimeoutInvoker = self.__eventBus.installTimer(
            frequency=10, handler=self._epaperTimeout, oneShot=True)

    def buttonPressed(self, button):
        log.debug(f"Button press detected for {button}")
        super().buttonPressed(button)

    def _epaperKeepAlive(self):
        if not self._epaperTimeoutInvoker.isQueued:
            log.debug('Waking up epaper display...')
            self._epd.init(self._epd.lut_partial_update)
        self._epaperTimeoutInvoker.reset()

    def _epaperTimeout(self):
        log.debug('Putting epaper display to sleep...')
        self._epd.sleep()

    def _buttonPressHandler(self, channel: int):
        # This happens on the GPIO interrupt thread, so to isolate threads,
        # we keep this local and safeInvoke() the actual base class
        # buttonPressed method call
        sleep(0.025)
        if not GPIO.input(channel):
            button = self._buttonMap.get(channel)
            if button is not None:
                self.__eventBus.safeInvoke(self.buttonPressed, button)

    def redraw(self):
        log.debug('rendering image')
        origImage = self.image.copy()
        super().redraw()
        log.debug('DONE rendering image')

        diff = ImageChops.difference(origImage, self.image)
        bbox = diff.getbbox()

        if bbox is not None:
            self._epaperKeepAlive()
            buffer = self._epd.getbuffer(self.image)
            self._epd.display(buffer)

        # self._epd.ClearWin(50, 50, 100, 60, 0)

        # buffer = self._epd.getbuffer(self.image)
        # self._epd.display(buffer)
