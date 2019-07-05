#pylint: disable=import-error
import board
import busio
import adafruit_bme280
#pylint: enable=import-error

import time
from interfaces import Hardware

class PhysicalHardware(Hardware):

    def __init__(self):
        super().__init__("PhysicalHardware")

        # Create library object using our Bus I2C port
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, address=0x76)

    # Returns temperature in degF
    def getTemperature(self):
        return self.bme280.temperature*9.0/5.0+32.0

    # Returns pressure in hPa
    def getPressure(self):
        return self.bme280.pressure

    # Returns humidity in relative %
    def getHumidity(self):
        return self.bme280.humidity

    # Set the underlying hardware heating mode
    def setModeHeat(self):
        print("Setting heat mode")

    # Set the underlying hardware to cooling
    def setModeCool(self):
        print("Setting cool mode")

    # Set the underlying hardware to fan only operation
    def setModeFan(self):
        print("Setting fan mode")


