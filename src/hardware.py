# pylint: disable=import-error
import board
import smbus
import busio
import adafruit_bme280
import RPi.GPIO as GPIO
# pylint: enable=import-error

from enum import Enum
from time import sleep

from src.logging import log
from src.generics import GenericLcdDisplay, GenericButton, \
    CounterBasedInvoker, GenericThermostatDriver, GenericEnvironmentSensor, \
    GenericRelay
from src.events import EventBus
from src.thermostat import ThermostatStateChangedEvent, ThermostatState


class Lcd1602Display(GenericLcdDisplay):

    # Modified version of the driver from
    # https://github.com/sunfounder/SunFounder_SensorKit_for_RPi2.git
    def __init__(self, addr, width, height):
        super().__init__(width, height)

        self.__smbus = smbus.SMBus(1)
        self.__lcdAddr = addr
        self.__blen = 1  # Hard-coding this, not sure what other options do

        self.__send_command(0x33)  # Must initialize to 8-line mode at first
        sleep(0.005)
        self.__send_command(0x32)  # Then initialize to 4-line mode
        sleep(0.005)
        self.__send_command(0x28)  # 2 Lines & 5*7 dots
        sleep(0.005)
        self.__send_command(0x0C)  # Enable display without cursor
        sleep(0.005)
        self.__send_command(0x01)  # Clear Screen
        self.__smbus.write_byte(self.__lcdAddr, 0x08)

    def __write_word(self, addr, data):
        temp = data
        if self.__blen == 1:
            temp |= 0x08
        else:
            temp &= 0xF7
        self.__smbus.write_byte(addr, temp)

    def __send(self, buf, op):
        buf |= op                # RS = 0, RW = 0, EN = 1
        self.__write_word(self.__lcdAddr, buf)
        sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.__write_word(self.__lcdAddr, buf)

    def __send_command(self, comm):
        # Send last 4 bits first, then send the first 4 bits
        self.__send(comm & 0xF0, 0x04)
        self.__send((comm & 0x0f) << 4, 0x04)

    def __send_data(self, data):
        # Send last 4 bits first, then send the first 4 bits
        self.__send(data & 0xF0, 0x05)
        self.__send((data & 0x0f) << 4, 0x05)

    def __clear(self):
        self.__send_command(0x01)  # Clear Screen

    def __openlight(self):  # Enable the backlight
        self.__smbus.write_byte(self.__lcdAddr, 0x08)
        self.__smbus.close()

    def __write(self, x, y, str):
        x = min(self.width-1, max(0, x))
        y = min(self.height-1, max(0, y))

        # Move cursor
        if y < 2:
            addr = 0x80 + 0x40 * y + x
        else:
            addr = 0x80 + self.width + 0x40 * (y-2) + x
        self.__send_command(addr)

        for chr in str:
            self.__send_data(ord(chr))

    def commit(self):
        """ Commits all pending changes to the display """
        results = super().commit()
        for i in range(len(results)):
            for change in results[i]:
                self.__write(change[0], i, change[1])


class SimplePushButton(GenericButton):
    """ A physical button provided to the user """

    def __init__(self, id: int, pin: int):
        super().__init__(id)
        self.__pin = pin
        self.__isPressed = False

        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def query(self):
        """ Returns whether the button was pressed since the last
        call to query() """
        isPressed = bool(GPIO.input(self.__pin))
        rtn = isPressed and not self.__isPressed
        self.__isPressed = isPressed
        return rtn


class Bm280EnvironmentSensor(GenericEnvironmentSensor):

    def __init__(self):
        self.__i2c = busio.I2C(board.SCL, board.SDA)
        self.__bme280 = \
            adafruit_bme280.Adafruit_BME280_I2C(self.__i2c, address=0x76)

    @property
    def temperature(self):
        return self.__bme280.temperature*9.0/5.0+32.0

    @property
    def pressure(self):
        return self.__bme280.pressure

    @property
    def humidity(self):
        return self.__bme280.humidity


class PanasonicAgqRelay(GenericRelay):

    def __init__(self, function: ThermostatState, pinIn: int, pinOut: int):
        super().__init__(function)
        self.__pinIn = pinIn
        self.__pinOut = pinOut

        GPIO.setup(self.__pinIn, GPIO.OUT)
        GPIO.setup(self.__pinOut, GPIO.OUT)
        self.openRelay()

    def openRelay(self):
        super().openRelay()

        # NEGATIVE 3V from IN->OUT opens the relay
        GPIO.output(self.__pinIn, False)
        GPIO.output(self.__pinOut, True)
        sleep(0.1)
        GPIO.output(self.__pinOut, False)

    def closeRelay(self):
        super().closeRelay()

        # POSITIVE 3V from IN->OUT opens the relay
        GPIO.output(self.__pinIn, True)
        sleep(0.1)
        GPIO.output(self.__pinIn, False)


class HardwareThermostatDriver(GenericThermostatDriver):

    def __init__(self, eventBus: EventBus):
        GPIO.setmode(GPIO.BCM)

        super().__init__(
            eventBus=eventBus,
            lcd=Lcd1602Display(0x27, 20, 4),
            sensor=Bm280EnvironmentSensor(),
            buttons=(
                SimplePushButton(1, 21),
                SimplePushButton(2, 20),
                SimplePushButton(3, 16),
                SimplePushButton(4, 12),
            ),
            relays=(
                PanasonicAgqRelay(ThermostatState.FAN, 5, 17),
                PanasonicAgqRelay(ThermostatState.HEATING, 6, 27),
                PanasonicAgqRelay(ThermostatState.COOLING, 13, 22),
            )
        )
