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
from src.thermostat import ThermostatStateChangedEvent, ThermostatState, \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


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


class HardwareDriver(EventHandler):

    class CounterBasedInvoker:

        def __init__(self, ticks: int, handlers: list):
            self.__ticks = ticks
            self.__handlers = handlers
            self.__lastHandler = 0
            self.__counter = 0

        def increment(self, execute=True):
            if 0 == self.__counter % self.__ticks:
                if execute:
                    self.invokeCurrent()
                self.__lastHandler = \
                    (self.__lastHandler + 1) % len(self.__handlers)
            self.__counter += 1

        def invokeCurrent(self):
            self.__handlers[self.__lastHandler]()

        def reset(self, handler: int=None):
            self.__lastHandler = handler or 0
            self.__counter = 1

    def __init__(self, eventBus: EventBus):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(5, GPIO.OUT)
        GPIO.setup(6, GPIO.OUT)
        GPIO.setup(13, GPIO.OUT)
        GPIO.setup(19, GPIO.OUT)

        self.__buttons = (
            Button('Mode', 16),
            Button('Up', 20),
            Button('Down', 21),
            Button('Enter', 12),
        )

        loopSleep = 0.05
        self.__lastTemperature = 0
        self.__lastHumidity = 0
        self.__lastPressure = 0
        self.__lastState = ThermostatState.OFF

        self.__sampleInvoker = HardwareDriver.CounterBasedInvoker(
            ticks=int(5/loopSleep), handlers=[self.__sampleSensors])
        self.__drawLcdInvoker = HardwareDriver.CounterBasedInvoker(
            ticks=int(0.1/loopSleep), handlers=[self.__drawLcdDisplay])
        self.__drawRowTwoInvoker = HardwareDriver.CounterBasedInvoker(
            ticks=int(3/loopSleep),
            handlers=[self.__drawRowTwoTarget, self.__drawRowTwoState])

        self.__rotateRowTwoInterval = int(3/loopSleep)
        self.__buttonHandler = self.__buttonHandlerDefault

        self.__settings = Settings()
        self.__i2c = busio.I2C(board.SCL, board.SDA)
        self.__bme280 = \
            adafruit_bme280.Adafruit_BME280_I2C(self.__i2c, address=0x76)
        self.__lcd = Lcd1602Display(0x27, 16, 2)

        super().__init__(eventBus, loopSleep)
        super()._subscribe(
            SettingsChangedEvent, self.__processSettingsChanged)
        super()._subscribe(
            ThermostatStateChangedEvent, self.__processStateChanged)

    def processEvents(self):
        super().processEvents()

        # Always scan for button presses
        self.__processButtons()

        # Update the LCD display with the current page's content
        self.__drawLcdInvoker.increment()
        self.__drawRowTwoInvoker.increment(execute=False)

        # Only update measurements at the sample interval
        self.__sampleInvoker.increment()

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        log.debug(f"HardwareDriver: new settings: {event.settings}")
        self.__settings = event.settings

    def __processStateChanged(self, event: ThermostatStateChangedEvent):
        log.debug(f"HardwareDriver: new state: {event.state}")
        GPIO.output(5, event.state == ThermostatState.FAN)
        GPIO.output(6, event.state == ThermostatState.HEATING)
        GPIO.output(13, event.state == ThermostatState.COOLING)
        GPIO.output(19, event.state == ThermostatState.OFF)
        self.__lastState = event.state
        self.__drawLcdInvoker.reset()

    def __sampleSensors(self):
        self.__lastTemperature = self.__bme280.temperature*9.0/5.0+32.0
        self.__lastPressure = self.__bme280.pressure
        self.__lastHumidity = self.__bme280.humidity
        super()._fireEvent(TemperatureChangedEvent(self.__lastTemperature))
        super()._fireEvent(PressureChangedEvent(self.__lastPressure))
        super()._fireEvent(HumidityChangedEvent(self.__lastHumidity))

    def __buttonHandlerDefault(self, button: Button):
        log.debug(f"DefaultButtonHandler saw {button.name}")
        if 'Mode' == button.name:
            self.__drawRowTwoInvoker.reset(1)
            self.__settings = self.__settings.clone(mode=Settings.Mode(
                (int(self.__settings.mode.value)+1) % len(Settings.Mode)))
            super()._fireEvent(SettingsChangedEvent(self.__settings))
        elif 'Up' == button.name:
            self.__drawRowTwoInvoker.reset(0)
            if Settings.Mode.HEAT == self.__settings.mode:
                self.__settings = self.__settings.clone(
                    comfortMin=self.__settings.comfortMin + 1)
                super()._fireEvent(SettingsChangedEvent(self.__settings))
            if Settings.Mode.COOL == self.__settings.mode:
                self.__settings = self.__settings.clone(
                    comfortMax=self.__settings.comfortMax + 1)
                super()._fireEvent(SettingsChangedEvent(self.__settings))
        elif 'Down' == button.name:
            self.__drawRowTwoInvoker.reset(0)
            if Settings.Mode.HEAT == self.__settings.mode:
                self.__settings = self.__settings.clone(
                    comfortMin=self.__settings.comfortMin - 1)
                super()._fireEvent(SettingsChangedEvent(self.__settings))
            if Settings.Mode.COOL == self.__settings.mode:
                self.__settings = self.__settings.clone(
                    comfortMax=self.__settings.comfortMax - 1)
                super()._fireEvent(SettingsChangedEvent(self.__settings))

    def __processButtons(self):
        for button in self.__buttons:
            if button.query():
                self.__buttonHandler(button)

    def __drawRowTwoTarget(self):
        # 0123456789012345
        # Target:  ## / ##
        heat = self.__settings.comfortMin
        cool = self.__settings.comfortMax
        self.__lcd.update(1, 0, f'Target:  {heat:2.0f} / {cool:2.0f}')

    def __drawRowTwoState(self):
        # 0123456789012345
        # State:   COOLING
        state = str(self.__lastState).replace('ThermostatState.', '')
        self.__lcd.update(1, 0, f'State: {state:>9s}')

    def __drawLcdDisplay(self):
        # 0123456789012345
        # Now: ##.#   AUTO
        now = self.__lastTemperature
        mode = str(self.__settings.mode).replace('Mode.', '')
        self.__lcd.update(0, 0, f'Now: {now:4.1f}{mode:>7s}')
        self.__drawRowTwoInvoker.invokeCurrent()
        self.__lcd.commit()
