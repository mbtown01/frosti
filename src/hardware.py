# pylint: disable=import-error
import board
import busio
import adafruit_bme280
# pylint: enable=import-error

from queue import Queue
from src.events import EventBus, EventHandler
from src.thermostat import \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


class SensorDriver(EventHandler):
    def __init__(self, eventBus: EventBus):
        loopSleep = 0.05
        self.__sampleInterval = int(5/loopSleep)
        self.__counter = 0
        self.__i2c = busio.I2C(board.SCL, board.SDA)
        self.__bme280 = \
            adafruit_bme280.Adafruit_BME280_I2C(self.__i2c, address=0x76)

        super().__init__(eventBus, loopSleep)

    def processEvents(self):
        super().processEvents()

        # Only update measurements at the sample interval
        self.__counter += 1
        if 0 == self.__counter % self.__sampleInterval:
            super()._fireEvent(TemperatureChangedEvent(
                self.__bme280.temperature*9.0/5.0+32.0))
            super()._fireEvent(PressureChangedEvent(
                self.__bme280.pressure))
            super()._fireEvent(HumidityChangedEvent(
                self.__bme280.humidity))

        # Additional scanning should be done for user buttons here
