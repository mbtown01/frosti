import RPi.GPIO as GPIO
import smbus

from time import sleep


class LM5024Driver:

    DEVICE_CONFIG_0 = 0x00
    DEVICE_CONFIG_1 = 0x01
    LED_CONFIG_0 = 0x02
    BANK_BRIGHTNESS = 0x03
    BANK_A_COLOR = 0x04
    BANK_B_COLOR = 0x05
    BANK_C_COLOR = 0x06

    # 8 LED brightness registers, increasing by one byte each
    LED_BRIGHTNESS_0 = 0x07

    # 24 out color addresses, increasing by one byte each
    OUT_COLOR_0 = 0x0f

    RESET = 0x27

    def __init__(self):
        self.__addr = 0x3c
        self.__bus = smbus.SMBus(1)
        self.__bus.write_byte_data(self.__addr, self.DEVICE_CONFIG_0, 0x40)
        self.__bus.write_byte_data(self.__addr, self.DEVICE_CONFIG_1, 0x3c)

    def _buildHardwareColorList(self, rgbColor: int):
        red = (rgbColor & 0xff0000) >> 16
        green = (rgbColor & 0x00ff00) >> 8
        blue = (rgbColor & 0x0000ff)
        return [green, red, blue]

    def breathe(self, rgbColor: int, cycles: int):
        hardwareColor = self._buildHardwareColorList(rgbColor)
        self.__bus.write_byte_data(self.__addr, self.LED_CONFIG_0, 0xff)
        self.__bus.write_i2c_block_data(
            self.__addr, self.BANK_A_COLOR, hardwareColor)

        for j in range(cycles):
            for i in range(40, 250, 10):
                self.__bus.write_byte_data(
                    self.__addr, self.BANK_BRIGHTNESS, i)
                sleep(0.1)
            for i in range(250, 40, -10):
                self.__bus.write_byte_data(
                    self.__addr, self.BANK_BRIGHTNESS, i)
                sleep(0.1)

    def dance(self, rgbColor1: int, rgbColor2: int, brightness: int, cycles: int):
        self.__bus.write_byte_data(self.__addr, self.LED_CONFIG_0, 0x00)
        self.__bus.write_i2c_block_data(
            self.__addr, self.LED_BRIGHTNESS_0, [brightness]*8)

        colorList = [
            self._buildHardwareColorList(rgbColor1),
            self._buildHardwareColorList(rgbColor2),
        ]

        for j in range(cycles):
            for i in range(8):
                hardwareColor = colorList[(j+i) % 2]
                led = self.OUT_COLOR_0+3*i
                self.__bus.write_i2c_block_data(
                    self.__addr, led, hardwareColor)
            sleep(0.2)
