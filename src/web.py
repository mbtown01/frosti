from flask import Flask
from physical import PhysicalHardware

app = Flask(__name__)

hardware = PhysicalHardware()


@app.route('/api/version')
def hello_world():
    return "rpt-0.1"


@app.route('/api/sensors/temperature')
def sensor_temperature():
    return "{}".format(hardware.getTemperature())


@app.route('/api/sensors/pressure')
def sensor_pressure():
    return "{}".format(hardware.getPressure())


@app.route('/api/sensors/humidity')
def sensor_humidity():
    return "{}".format(hardware.getHumidity())

if __name__ == '__main__':
    app.run("0.0.0.0", 5000)