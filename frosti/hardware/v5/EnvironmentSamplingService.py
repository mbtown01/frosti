import board
import busio
import adafruit_bme280

from frosti.services import EnvironmentSamplingService


class EnvironmentSamplingService(EnvironmentSamplingService):
    """ Holds a GenericEnvironmentSensor and at a specified frequency
    takes a sampling and fires a SensorDataChangedEvent """

    def __init__(self):
        super().__init__()

        self.__i2c = busio.I2C(board.SCL, board.SDA)
        self.__bme280 = \
            adafruit_bme280.Adafruit_BME280_I2C(self.__i2c, address=0x76)

    def _getRawTemperature(self):
        return self.__bme280.temperature * 9.0 / 5.0 + 32.0

    def _getRawPressure(self):
        return self.__bme280.pressure

    def _getRawHumidity(self):
        return self.__bme280.humidity
