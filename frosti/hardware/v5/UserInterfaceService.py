import RPi.GPIO as GPIO

from time import sleep, time_ns
from PIL import ImageChops
# from PIL import ImageFont, ImageDraw, Image

from frosti.services.UserInterfaceService \
    import UserInterfaceService as BaseUserInterfaceService, HardwareButton
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
            rgbColorList=[0x33ff33], cycles=2, rate=0.025, brightMin=0,
            brightMax=160)

        # self._ledRingDriver.rainbow(cycles=2)
        self._ledRingDriver.breathe(
            rgbColorList=self._ledRingDriver.rgbRainbowList[::32],
            cycles=2*160//5, rate=0.025, brightMin=200, brightMax=201,
            brightStep=1)

        self._ledRingDriver.chase(
            rgbColorList=[0]*15 + [0xff00ff], brightnessList=[200],
            rate=0.0125, cycles=4)
        self._ledRingDriver.chase(
            rgbColorList=[0xff0000]*8 + [0x0000ff]*8,
            brightnessList=[175], cycles=8)

        self._ledRingDriver.chase(
            rgbColorList=[0xff0000, 0xff0000, 0x0000ff, 0x0000ff], cycles=4)

        self._ledRingDriver.chase(
            rgbColorList=[
                0xff0000, 0xff0000, 0xff0000, 0xff0000,
                0x0000ff, 0x0000ff, 0x0000ff, 0x0000ff], cycles=4)

        super().__init__(self._epd.height, self._epd.width)

        self._displayBuf = [0xFF] * (int(self._epd.width/8) * self._epd.height)

        self._buttonMap = {
            23: HardwareButton.UP,
            27: HardwareButton.ENTER,
            22: HardwareButton.DOWN,
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

    def buttonPressed(self, button: HardwareButton):
        log.debug(f"Button press detected for {button}")
        if HardwareButton.ENTER == button:
            self._ledRingDriver.breathe(
                rgbColorList=[0xffffff], cycles=1, rate=0.005, brightMin=0,
                brightMax=160)
        elif HardwareButton.UP == button:
            self._ledRingDriver.breathe(
                rgbColorList=[0xffffff], cycles=1, rate=0.005, brightMin=0,
                brightMax=160)
        elif HardwareButton.DOWN == button:
            self._ledRingDriver.breathe(
                rgbColorList=[0xffffff], cycles=1, rate=0.005, brightMin=0,
                brightMax=160)
        else:
            raise RuntimeError(f"Unknown button: {button}")

        super().buttonPressed(button)

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
        lastImage = self.image.copy()
        super().redraw()
        diff = ImageChops.difference(lastImage, self.image)
        bbox = diff.getbbox()

        if bbox is not None:
            # Display is changing, so wake it up and/or reset the timer to
            # shut it back down again
            if not self._epaperTimeoutInvoker.isQueued:
                log.debug('Waking up epaper display...')
                self._epd.init(self._epd.lut_partial_update)
            self._epaperTimeoutInvoker.reset()

            start = time_ns()
            self._updateDisplayBuf(bbox)
            log.debug(f"_updateDisplayBuf() took {(time_ns()-start)/1e6} ms")
            self._epd.display(self._displayBuf)
