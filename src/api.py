import board
import time
import busio
import adafruit_bme280

class HardwareApi:

    def __init__(self):
        # Create library object using our Bus I2C port
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(self.i2c, address=0x76)

    # Returns temperature in degC
    def getTemperature(self):
        return self.bme280.temperature

    # Returns pressure in hPa
    def getPressure(self):
        return self.bme280.pressure

    # Returns humidity in relative %
    def getHumidity(self):
        return self.bme280.humidity

API_INSTANCE = HardwareApi()