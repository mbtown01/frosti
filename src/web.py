from flask import Flask
from queue import Queue
from threading import Thread

from physical import PhysicalDriver
from settings import Settings
from interfaces import FloatEvent, EventType
from driver import LogicDriver

app = Flask(__name__)

# @app.route('/api/version')
# def hello_world():
#     return "rpt-0.1"


# @app.route('/api/sensors/temperature')
# def sensor_temperature():
#     return "{}".format(hardware.getTemperature())


# @app.route('/api/sensors/pressure')
# def sensor_pressure():
#     return "{}".format(hardware.getPressure())


# @app.route('/api/sensors/humidity')
# def sensor_humidity():
#     return "{}".format(hardware.getHumidity())

if __name__ == '__main__':
    contolQueue = Queue()
    eventQueue = Queue()

    settings = Settings()
    logicDriver = LogicDriver(settings)
    physicalDriver = PhysicalDriver()

    hardwareThread = Thread(
        target=physicalDriver.exec,
        name='Physical Driver',
        args=(contolQueue, eventQueue))
    hardwareThread.daemon = True
    hardwareThread.start()

    driverThread = Thread(
        target=logicDriver.exec,
        name='Logic Driver',
        args=(contolQueue, eventQueue))
    driverThread.daemon = True
    driverThread.start()

    app.run("0.0.0.0", 5000)
