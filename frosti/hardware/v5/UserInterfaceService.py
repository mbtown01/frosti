import RPi.GPIO as GPIO
import smbus

from time import sleep
from PIL import ImageChops
# from PIL import ImageFont, ImageDraw, Image

from frosti.services.UserInterfaceService \
    import UserInterfaceService as BaseUserInterfaceService
from frosti.core import ServiceProvider, EventBus
from frosti.hardware.epd2in9 import EPD
from frosti.logging import log

RING_ADDR_LEFT = 0x27
RING_ADDR_RIGHT = 0x27
RING_ADDR_BOTH = 0x3c


class LP5024Driver:
    """ Hardly a driver, this is just a wrapper over the I2C interface for the
    LED controller to make it easier to work with

    From the LP5024 datasheet https://www.ti.com/lit/ds/symlink/lp5024.pdf
    """

    # Addresses
    DEVICE_CONFIG = 0x00
    LED_CONFIG = 0x02
    BANK_BRIGHTNESS = 0x03
    BANK_COLOR = 0x04
    LED_BRIGHTNESS = 0x07  # (there are 8 of these)
    LED_COLOR = 0x0f  # (there are 24 of these)
    RESET = 0x27

    def __init__(self, addr: int, **setupArgs):
        self._addr = addr
        self._bus = smbus.SMBus(1)
        self.setup(**setupArgs)

    def setup(self, *,
              enable: bool = False,
              logScale: bool = True,
              powerSave: bool = True,
              autoIncrement: bool = True,
              pwmDithering: bool = True,
              maxCurrent: bool = False,
              ledGlobalOff: bool = False
              ):
        """ Configure the driver with the provided options.  The default
        values provided are the defaults from the datasheet after a reset

            enable:
                1 = LP50xx enabled
                0 = LP50xx not enabled
            logScale:
                1 = Logarithmic scale dimming curve enabled
                0 = Linear scale dimming curve enabled
            powerSave:
                1 = Automatic power-saving mode enabled
                0 = Automatic power-saving mode not enabled
            autoIncrement:
                1 = Automatic increment mode enabled
                0 = Automatic increment mode not enabled
            pwmDitering:
                1 = PWM dithering mode enabled
                0 = PWM dithering mode not enabled
            maxCurrent:
                1 = Output maximum current IMAX = 35 mA.
                0 = Output maximum current IMAX = 25.5 mA.
            ledGlobalOff:
                1 = Shut down all LEDs
                0 = Normal operation
        """

        c0Config, c1Config = 0, 0
        c0Config |= 0x40 if enable else 0
        c1Config |= 0x20 if logScale else 0
        c1Config |= 0x10 if powerSave else 0
        c1Config |= 0x08 if autoIncrement else 0
        c1Config |= 0x04 if pwmDithering else 0
        c1Config |= 0x02 if maxCurrent else 0
        c1Config |= 0x01 if ledGlobalOff else 0

        self._bus.write_i2c_block_data(
            self._addr, self.DEVICE_CONFIG, [c0Config, c1Config])

    def setBankControlled(self, bitfield: int):
        """ Takes the bitfield (8-bit) and uses it as a truth vector to
        specify which LEDs are bank controlled """
        self._bus.write_byte_data(self._addr, self.LED_CONFIG, bitfield)

    def setBankColor(self, rgbColor: int):
        """ Sets the bank color """
        hardwareColor = self._buildHardwareColorList(rgbColor)
        self._bus.write_i2c_block_data(
            self._addr, self.BANK_COLOR, hardwareColor)

    def setBankBrightness(self, brightness: int):
        """ Sets the bank brightness level """
        self._bus.write_byte_data(
            self._addr, self.BANK_BRIGHTNESS, brightness)

    def setLedColor(self, rgbColorList: list):
        """ Sets the color for each of the 8 LEDs """
        if len(rgbColorList) != 8:
            raise RuntimeError("Expected 8 RGB color values")
        hardwareColorList = list(
            item for sublist in rgbColorList
            for item in self._buildHardwareColorList(sublist))
        self._bus.write_i2c_block_data(
            self._addr, self.LED_COLOR, hardwareColorList)

    def setLedBrightness(self, brightnessList: list):
        """ Sets the brightness for each of the 8 LEDs """
        if len(brightnessList) != 8:
            raise RuntimeError("Expected 8 brightness values")
        self._bus.write_i2c_block_data(
            self._addr, self.LED_BRIGHTNESS, brightnessList)

    def _buildHardwareColorList(self, rgbColor: int):
        """ Convert a standard rgb integer to a 3-byte array destined for the
        LED driver.  Note that our driver hardware is actually wired GRB """
        red = (rgbColor & 0xff0000) >> 16
        green = (rgbColor & 0x00ff00) >> 8
        blue = (rgbColor & 0x0000ff)
        return [green, red, blue]


class LedRingDriver:

    def __init__(self):
        self._bothCircles = LP5024Driver(0x3c, enable=True)
        self._leftCircle = LP5024Driver(0x28, enable=True)
        self._rightCircle = LP5024Driver(0x29, enable=True)

        incrementList = [
            0x000100, -0x010000,
            0x000001, -0x000100,
            0x010000, -0x000001,
        ]

        color = 0xff0000
        self._rainbowColorList = list()
        for increment in incrementList:
            for i in range(255):
                self._rainbowColorList.append(color+increment*i)
            color += increment*(255)

    def breathe(self,
                rgbColor: int,
                *,
                brightMin: int = 40,
                brightMax: int = 250,
                brightStep: int = 5,
                cycles: int = 1,
                rate: float = 0.05):
        self._bothCircles.setBankColor(rgbColor)
        self._bothCircles.setBankControlled(0b11111111)

        for j in range(cycles):
            for i in range(brightMin, brightMax, brightStep):
                self._bothCircles.setBankBrightness(i)
                sleep(rate)
            for i in range(brightMax, brightMin, -brightStep):
                self._bothCircles.setBankBrightness(i)
                sleep(rate)

        self._bothCircles.setBankBrightness(brightMin)

    def breatheRainbow(self,
                       *,
                       cycles: int = 1,
                       rate: float = 0.025):
        self._bothCircles.setBankControlled(0b11111111)
        self._bothCircles.setBankBrightness(230)

        colorList = self._rainbowColorList
        c = 0
        for j in range(cycles):
            for i in range(40, 250, 5):
                self._bothCircles.setBankColor(colorList[c % len(colorList)])
                self._bothCircles.setBankBrightness(i)
                c += 16
                sleep(rate)
            for i in range(250, 40, -5):
                self._bothCircles.setBankColor(colorList[c % len(colorList)])
                self._bothCircles.setBankBrightness(i)
                c += 16
                sleep(rate)

    def dance(self,
              rgbColorList: list,
              *,
              brightness: int = 230,
              cycles: int = 1,
              rate: float = 0.05):
        self._bothCircles.setBankControlled(0b00000000)
        self._bothCircles.setLedBrightness([brightness]*8)

        for j in range(cycles):
            localColorList = list(
                rgbColorList[(j+i) % len(rgbColorList)] for i in range(8))
            self._bothCircles.setLedColor(localColorList)
            sleep(rate)

    def chase(self,
              rgbColorList: list,
              brightnessList: list,
              *,
              cycles: int = 1,
              rate: float = 0.025):
        self._bothCircles.setBankControlled(0x00)
        self._bothCircles.setLedBrightness([0]*8)
        self._bothCircles.setLedColor([0]*8)

        if len(rgbColorList) != 16:
            raise RuntimeError("Expected 16 RGB color values")
        if len(brightnessList) != 16:
            raise RuntimeError("Expected 16 brightness values")

        for j in range(16*cycles):
            leftCircleRgbColorList = list(
                rgbColorList[(a+j) % 16] for a in range(8))
            leftCircleBrightness = list(
                brightnessList[(a+j) % 16] for a in range(8))
            rightCircleRgbColorList = list(
                rgbColorList[(a+j+8) % 16] for a in range(8))
            rightCircleBrightness = list(
                brightnessList[(a+j+8) % 16] for a in range(8))
            self._leftCircle.setLedColor(leftCircleRgbColorList)
            self._leftCircle.setLedBrightness(leftCircleBrightness)
            self._rightCircle.setLedColor(rightCircleRgbColorList)
            self._rightCircle.setLedBrightness(rightCircleBrightness)
            sleep(rate)


class UserInterfaceService(BaseUserInterfaceService):

    def __init__(self):
        super().__init__()

        self._ledRingDriver = LedRingDriver()
        # self._ledRingDriver.breathe(
        #     0x33ff33, cycles=2, rate=0.01, brightMin=0, brightMax=160)
        # self._ledRingDriver.breatheRainbow(cycles=1)
        # self._ledRingDriver.chase(
        #     [0x11ff11] + [0]*15, [230]*16, cycles=16)
        self._ledRingDriver.chase(
            [0xff0000]*8 + [0x0000ff]*8, [230]*16, cycles=120)
        self._ledRingDriver.dance(
            [0xff0000, 0xff0000, 0x0000ff, 0x0000ff], cycles=40)
        self._ledRingDriver.dance(
            [0xff0000, 0xff0000, 0xff0000, 0xff0000,
             0x0000ff, 0x0000ff, 0x0000ff, 0x0000ff], cycles=40)

        self._epd = EPD()
        self._epd.init(self._epd.lut_partial_update)
        self._epd.Clear(0xFF)
        self._epd.Clear(0x00)
        self._epd.Clear(0xFF)

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

    def redraw(self):
        origImage = self.image.copy()
        super().redraw()
        diff = ImageChops.difference(origImage, self.image)
        bbox = diff.getbbox()

        if bbox is not None:
            self._epaperKeepAlive()
            buffer = self._epd.getbuffer(self.image)
            self._epd.display(buffer)

        # self._epd.ClearWin(50, 50, 100, 60, 0)

        # buffer = self._epd.getbuffer(self.image)
        # self._epd.display(buffer)
