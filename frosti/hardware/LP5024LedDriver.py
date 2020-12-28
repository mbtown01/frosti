import RPi.GPIO as GPIO
import smbus

from time import sleep


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
