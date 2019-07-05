from interfaces import Hardware
from settings import Settings
from collections import deque
import time
from queue import Queue


def exec(hardware: Hardware, settings: Settings, sampleWait=1, sampleCount=16):
    readings = Queue(0)

    while 1:
        time.sleep(sampleWait)

        # Get the latest temperature reading and push it into the queue we're
        # using to measure in a rolling time window.  If there aren't enough
        # samples in the window, move on to the next sample
        temperature = hardware.getTemperature()
        readings.put(temperature)
        if len(readings) < sampleCount:
            continue

        # Treat the list like a queue of readings to get a rolling average
        temperature = sum(readings) / len(readings)
        readings.get()

        # If we are over the temperature goal, enable the fan
        if temperature > settings.getCoolThreshold():
            hardware.setModeCool()

        # If we are under the min temperature, disable the fan
        if temperature <= settings.getHeatThreshold():
            hardware.setModeHeat()
