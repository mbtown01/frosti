# pylint: disable=import-error
import board
import smbus
import busio
import adafruit_bme280
import RPi.GPIO as GPIO
# pylint: enable=import-error

from queue import Queue
from time import sleep

from src.logging import log
from src.generics import GenericLcdDisplay
from src.settings import Settings, SettingsChangedEvent
from src.events import EventBus, EventHandler, Event
from src.thermostat import \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


class Lcd1602Display(GenericLcdDisplay):

    # Modified version of the driver from
    # https://github.com/sunfounder/SunFounder_SensorKit_for_RPi2.git
    def __init__(self, addr, width, height):
        super().__init__(width, height)

        self.__smbus = smbus.SMBus(1)
        self.__lcdAddr = addr
        self.__width = width
        self.__height = height
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

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def __write_word(self, addr, data):
        temp = data
        if self.__blen == 1:
            temp |= 0x08
        else:
            temp &= 0xF7
        self.__smbus.write_byte(addr, temp)

    def __send_command(self, comm):
        # Send bit7-4 firstly
        buf = comm & 0xF0
        buf |= 0x04               # RS = 0, RW = 0, EN = 1
        self.__write_word(self.__lcdAddr, buf)
        sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.__write_word(self.__lcdAddr, buf)

        # Send bit3-0 secondly
        buf = (comm & 0x0F) << 4
        buf |= 0x04               # RS = 0, RW = 0, EN = 1
        self.__write_word(self.__lcdAddr, buf)
        sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.__write_word(self.__lcdAddr, buf)

    def __send_data(self, data):
        # Send bit7-4 firstly
        buf = data & 0xF0
        buf |= 0x05               # RS = 1, RW = 0, EN = 1
        self.__write_word(self.__lcdAddr, buf)
        sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.__write_word(self.__lcdAddr, buf)

        # Send bit3-0 secondly
        buf = (data & 0x0F) << 4
        buf |= 0x05               # RS = 1, RW = 0, EN = 1
        self.__write_word(self.__lcdAddr, buf)
        sleep(0.002)
        buf &= 0xFB               # Make EN = 0
        self.__write_word(self.__lcdAddr, buf)

    def __clear(self):
        self.__send_command(0x01)  # Clear Screen

    def __openlight(self):  # Enable the backlight
        self.__smbus.write_byte(0x27, 0x08)
        self.__smbus.close()

    def __write(self, x, y, str):
        x = min(self.__width-1, max(0, x))
        y = min(self.__height-1, max(0, y))

        # Move cursor
        addr = 0x80 + 0x40 * y + x
        self.__send_command(addr)

        for chr in str:
            self.__send_data(ord(chr))

    def commit(self):
        """ Commits all pending changes to the display """
        results = super().commit()
        for i in range(len(results)):
            for change in results[i]:
                self.__write(change[0], i, change[1])


class Button:
    """ A physical button provided to the user """

    def __init__(self, name: str, pin: int):
        self.__name = name
        self.__pin = pin
        self.__isPressed = False

        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    @property
    def name(self):
        return self.__name

    def query(self):
        """ Returns whether the button was pressed since the last
        call to query() """
        isPressed = bool(GPIO.input(self.__pin))
        rtn = isPressed and not self.__isPressed
        self.__isPressed = isPressed
        return rtn


class StatusPage:

    def __init__(self):
        self.__lastTemperature = 0
        self.__lastHumidity = 0
        self.__lastPressure = 0

    # 0123456789012345
    # Now: ##.#   AUTO
    # Target:  ## / ##

    def updateTemperature(self, temperature: float):
        self.__lastTemperature = temperature

    def write(self, settings: Settings, lcd: Lcd1602Display):
        now = self.__lastTemperature
        mode = str(settings.mode).replace("Mode.", "")
        heat = settings.comfortMin
        cool = settings.comfortMax
        lcd.update(0, 0, f'Now: {now:4.1f}{mode:>7s}')
        lcd.update(1, 0, f'Target:  {heat:2.0f} / {cool:2.0f}')
        lcd.commit()


class HardwareDriver(EventHandler):

    def __init__(self, eventBus: EventBus):
        GPIO.setmode(GPIO.BCM)

        self.__buttons = (
            Button('Mode', 16),
            Button('Up', 20),
            Button('Down', 21),
            Button('Enter', 12),
        )

        loopSleep = 0.05
        self.__statusPage = StatusPage()
        self.__currentPage = self.__statusPage
        self.__sampleInterval = int(5/loopSleep)
        self.__drawInterval = int(0.1/loopSleep)
        self.__settings = Settings()
        self.__counter = 0
        self.__i2c = busio.I2C(board.SCL, board.SDA)
        self.__bme280 = \
            adafruit_bme280.Adafruit_BME280_I2C(self.__i2c, address=0x76)
        self.__lcd = Lcd1602Display(0x27, 20, 2)

        super().__init__(eventBus, loopSleep)
        super()._subscribe(
            SettingsChangedEvent, self.__processSettingsChanged)

    def processEvents(self):
        super().processEvents()

        # Always scan for button presses
        for button in self.__buttons:
            if button.query():
                pass

        self.__counter += 1

        # Update the LCD display with the current page's content
        if 0 == self.__counter % self.__drawInterval:
            self.__currentPage.write(self.__settings, self.__lcd)

        # Only update measurements at the sample interval
        if 0 == self.__counter % self.__sampleInterval:
            temperature = self.__bme280.temperature*9.0/5.0+32.0
            pressure = self.__bme280.pressure
            humidity = self.__bme280.humidity
            self.__statusPage.updateTemperature(temperature)
            super()._fireEvent(TemperatureChangedEvent(temperature))
            super()._fireEvent(PressureChangedEvent(pressure))
            super()._fireEvent(HumidityChangedEvent(humidity))

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        log.debug(f"HardwareDriver: new settings: {event.settings}")
        self.__settings = event.settings
