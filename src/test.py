import sensors.Sensors



while True:
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("\nTemperature: %0.1f F" % (bme280.temperature*9.0/5.0+32.0))
    print("Pressure: %0.1f hPa" % bme280.pressure)
    print("Altitude = %0.2f meters" % bme280.altitude)
    print("Humidity: %0.1f %%" % bme280.humidity)
    time.sleep(2)

msg = 'hello, world'
print(msg)