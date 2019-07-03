from flaskApp import app
from api import API_INSTANCE

@app.route('/api/version')
def hello_world():
    return "hello, world"

@app.route('/api/sensors/temperature')
def sensor_temperature():
   return "{}".format(API_INSTANCE.getTemperature())

@app.route('/api/sensors/pressure')
def sensor_pressure():
   return "{}".format(API_INSTANCE.getTemperature())

@app.route('/api/sensors/humidity')
def sensor_humidity():
   return "{}".format(API_INSTANCE.getHumidity())
