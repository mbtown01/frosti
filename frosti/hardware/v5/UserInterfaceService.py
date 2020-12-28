import RPi.GPIO as GPIO

from time import sleep, time_ns
from PIL import ImageChops
# from PIL import ImageFont, ImageDraw, Image

from frosti.services.UserInterfaceService \
    import UserInterfaceService as BaseUserInterfaceService
from frosti.core import ServiceProvider, EventBus
from frosti.hardware.epd2in9 import EPD
from frosti.hardware.LedRingDriver import LedRingDriver
from frosti.logging import log


class UserInterfaceService(BaseUserInterfaceService):

    def __init__(self):
        self._epd = EPD()
        self._epd.init(self._epd.lut_partial_update)
        self._epd.Clear(0xFF)
        self._epd.Clear(0x00)
        self._epd.Clear(0xFF)

        self._ledRingDriver = LedRingDriver(enable=True)
        # self._ledRingDriver.setup(enable=False)
        self._ledRingDriver.breathe(
            rgbColor=0x33ff33, cycles=2, rate=0.025, brightMin=0,
            brightMax=160)
        self._ledRingDriver.rainbow(cycles=2)
        self._ledRingDriver.chase(
            rgbColorList=[0x11ff11] + [0]*15,
            brightnessList=[230]*16, rate=0.0125,
            cycles=8)
        self._ledRingDriver.chase(
            rgbColorList=[0xff0000]*8 + [0x0000ff]*8,
            brightnessList=[175]*16,
            cycles=8)
        self._ledRingDriver.dance(
            rgbColorList=[0xff0000, 0xff0000, 0x0000ff, 0x0000ff],
            cycles=8)
        self._ledRingDriver.dance(
            rgbColorList=[
                0xff0000, 0xff0000, 0xff0000, 0xff0000,
                0x0000ff, 0x0000ff, 0x0000ff, 0x0000ff],
            cycles=8)

        super().__init__(self._epd.height, self._epd.width)

        self._displayBuf = [0xFF] * (int(self._epd.width/8) * self._epd.height)

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
        self._eventBus = self._getService(EventBus)

        self._epaperTimeoutInvoker = self._eventBus.installTimer(
            frequency=10, handler=self._epaperTimeout, oneShot=True)

    def buttonPressed(self, button):
        log.debug(f"Button press detected for {button}")
        if UserInterfaceService.Button.ENTER == button:
            self._ledRingDriver.breathe(
                rgbColor=0xffffff, cycles=2, rate=0.005, brightMin=0,
                brightMax=160)
        elif UserInterfaceService.Button.UP == button:
            self._ledRingDriver.breathe(
                rgbColor=0x0000ff, cycles=2, rate=0.005, brightMin=0,
                brightMax=160)
        elif UserInterfaceService.Button.DOWN == button:
            self._ledRingDriver.breathe(
                rgbColor=0xff0000, cycles=2, rate=0.005, brightMin=0,
                brightMax=160)
        else:
            raise RuntimeError(f"Unknown button: {button}")

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
                self._eventBus.safeInvoke(self.buttonPressed, button)

    def _updateDisplayBuf(self, bbox):
        (x1, y1, x2, y2) = bbox
        pixels = self.image.load()
        for y in range(y1, y2):
            mask = ~(0x80 >> (y % 8))
            newx = y
            for x in range(x1, x2):
                newy = self._epd.height - x - 1
                if pixels[x, y] == 0:
                    self._displayBuf[
                        (newx + newy*self._epd.width) // 8] &= mask
                else:
                    self._displayBuf[
                        (newx + newy*self._epd.width) // 8] |= ~mask

    def redraw(self):
        origImage = self.image.copy()
        super().redraw()
        diff = ImageChops.difference(origImage, self.image)
        bbox = diff.getbbox()

        if bbox is not None:
            self._epaperKeepAlive()
            # buffer = self._epd.getbuffer(self.image)
            # self._epd.display(buffer)

            start = time_ns()
            self._updateDisplayBuf(bbox)
            # pixels = self.image.load()
            # for y in range(y1, y2):
            #     mask = ~(0x80 >> (y % 8))
            #     newx = y
            #     for x in range(x1, x2):
            #         newy = self._epd.height - x - 1
            #         if pixels[x, y] == 0:
            #             self._displayBuf[
            #                 (newx + newy*self._epd.width) // 8] &= mask
            #         else:
            #             self._displayBuf[
            #                 (newx + newy*self._epd.width) // 8] |= ~mask
            log.debug(f"_updateDisplayBuf() took {(time_ns()-start)/1e6} ms")
            self._epd.display(self._displayBuf)
