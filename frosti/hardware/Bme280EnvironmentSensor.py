# pylint: disable=import-error
import board
import busio
import adafruit_bme280
# pylint: enable=import-error

from frosti.core.generics import GenericEnvironmentSensor


class Bme280EnvironmentSensor(GenericEnvironmentSensor):

    def __init__(self):
        self.__i2c = busio.I2C(board.SCL, board.SDA)
        self.__bme280 = \
            adafruit_bme280.Adafruit_BME280_I2C(self.__i2c, address=0x76)

    @property
    def temperature(self):
        return self.__bme280.temperature * 9.0 / 5.0 + 32.0

    @property
    def pressure(self):
        return self.__bme280.pressure

    @property
    def humidity(self):
        return self.__bme280.humidity
