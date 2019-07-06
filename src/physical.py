# pylint: disable=import-error
import board
import busio
import adafruit_bme280
# pylint: enable=import-error

from queue import Queue
from time import sleep
from interfaces import Event
from interfaces import EventType
from interfaces import FloatEvent


def driver(controlQueue: Queue, eventQueue: Queue):
    wait = 0.05
    sampleInterval = int(5/wait)
    counter = 0

    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = \
        adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

    while 0 == controlQueue.qsize():
        sleep(wait)
        counter += 1

        if 0 == counter % sampleInterval:
            eventQueue.put(
                FloatEvent(
                    EventType.TEMPERATURE,
                    bme280.temperature*9.0/5.0+32.0))
            eventQueue.put(
                FloatEvent(
                    EventType.PRESSURE,
                    bme280.pressure))
            eventQueue.put(
                FloatEvent(
                    EventType.HUMIDITY,
                    bme280.humidity))

        # Additional scanning should be done for user buttons here
