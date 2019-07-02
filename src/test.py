import board
import time
import busio
import adafruit_bme280

# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

# change this to match the location's pressure (hPa) at sea level
#bmp280.seaLevelhPa = 1040.0

while True:
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("\nTemperature: %0.1f F" % (bme280.temperature*9.0/5.0+32.0))
    print("Pressure: %0.1f hPa" % bme280.pressure)
    print("Altitude = %0.2f meters" % bme280.altitude)
    print("Humidity: %0.1f %%" % bme280.humidity)
    time.sleep(2)

msg = 'hello, world'
print(msg)