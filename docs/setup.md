# Developer Setup

RPT is based on python3.   I personally use pip3 for bringing in packages.  Depending on your development platform, you may have several ways of installing both python and your own packages. 

## On the RaspberryPi

```
sudo apt install python3 wiringpi python3-pip i2c-tools python3-smbus
```

# Required modules
```
pip3 install --user adafruit-circuitpython-bme280
pip3 install --user adafruit-blinka adafruit-circuitpython-charlcd
pip3 install --user flask influxdb requests pytest pytest-cov
pip3 install --user --upgrade ptvsd
```

## Setup a development environment

## Creating a new RaspberryPi image

## Debugging

Though it's not impossible, it's far better to have a dedicated development machine and not work directly on the RaspberryPi.  It's a great little computer, but just doesn't have much horsepower to really host an IDE.

At start-up, RPT checks to see if `uname -a` contains the 'armv' architecture.  If detected, RPT starts in hardware mode and assumes it's attached to an RPT board.  Otherwise, it assumes it's in simulation mode and uses the terminal as a fake LCD, using keys 1-4 as proxies for the 4 buttons.
