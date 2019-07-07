# pylint: disable=import-error
import board
import busio
import adafruit_bme280
# pylint: enable=import-error

from queue import Queue
from time import sleep
from interfaces import Event, EventType, EventBus, FloatEvent, EventHandler


# This class shoud be the combination of both button sensing as well
# as display since these are very likely related
class UserInterfaceDriver(EventHandler):
    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus)


class SensorDriver(EventHandler):
    def __init__(self, eventBus: EventBus):
        super().__init__(eventBus)

    def exec(self):
        wait = 0.05
        sampleInterval = int(5/wait)
        counter = 0

        i2c = busio.I2C(board.SCL, board.SDA)
        bme280 = \
            adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

        while True:
            sleep(wait)
            super()._processEvents()

            counter += 1
            if 0 == counter % sampleInterval:
                super()._putEvent(
                    FloatEvent(
                        EventType.TEMPERATURE,
                        bme280.temperature*9.0/5.0+32.0))
                super()._putEvent(
                    FloatEvent(
                        EventType.PRESSURE,
                        bme280.pressure))
                super()._putEvent(
                    FloatEvent(
                        EventType.HUMIDITY,
                        bme280.humidity))

            # Additional scanning should be done for user buttons here
