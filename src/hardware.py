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
from src.generics import GenericLcdDisplay, \
    GenericThermostatDriver, GenericEnvironmentSensor, \
    GenericRelay, ThermostatState
from src.events import EventBus, Event


class HD44780Display(GenericLcdDisplay):
    """ An HD44780 character based LCD display fronted by an i2c interface """

    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    # flags for backlight control
    LCD_BACKLIGHT = 0x08
    LCD_NOBACKLIGHT = 0x00

    CTRL_EN = 0b00000100  # Enable bit
    CTRL_RW = 0b00000010  # Read/Write bit
    CTRL_RS = 0b00000001  # Register select bit

    def __init__(self, addr, width, height):
        super().__init__(width, height)
        self.__addr = addr
        self.__bus = smbus.SMBus(1)
        self.__backlightState = self.LCD_BACKLIGHT
        self.__failCount = 0

        self.__hardReset()

    def __hardReset(self):
        self.__write(0x03)
        self.__write(0x03)
        self.__write(0x03)
        self.__write(0x02)

        self.__write(
            self.LCD_FUNCTIONSET | self.LCD_2LINE |
            self.LCD_5x8DOTS | self.LCD_4BITMODE)
        self.__write(self.LCD_DISPLAYCONTROL | self.LCD_DISPLAYON)
        self.__write(self.LCD_CLEARDISPLAY)
        self.__write(self.LCD_ENTRYMODESET | self.LCD_ENTRYLEFT)
        sleep(0.2)

    def __write_cmd(self, cmd):
        try:
            self.__bus.write_byte(self.__addr, cmd)
            sleep(0.0001)
            if self.__failCount:
                self.__failCount = 0
                self.__hardReset()
                self.clear()
                log.info("Re-connected to LCD, reset failuire count to zero")
        except:
            log.error(f"LCD __write_cmd failed, total={self.__failCount}")
            self.__failCount += 1

    # clocks EN to latch command
    def __strobe(self, data):
        self.__write_cmd(data | self.CTRL_EN | self.__backlightState)
        sleep(.0005)
        self.__write_cmd(((data & ~self.CTRL_EN) | self.__backlightState))
        sleep(.0001)

    def __write_four_bits(self, data):
        self.__write_cmd(data | self.__backlightState)
        self.__strobe(data)

    # write a command to lcd
    def __write(self, cmd, mode=0):
        self.__write_four_bits(mode | (cmd & 0xF0))
        self.__write_four_bits(mode | ((cmd << 4) & 0xF0))

    def __write_str(self, x, y, str):
        x = min(self.width-1, max(0, x))
        y = min(self.height-1, max(0, y))

        # Move cursor
        if y < 2:
            addr = 0x80 + 0x40 * y + x
        else:
            addr = 0x80 + self.width + 0x40 * (y-2) + x
        self.__write(addr)

        for char in str:
            self.__write(ord(char), self.CTRL_RS)

    def clear(self):
        """ Clear the contents of the LCD screen """
        super().clear()
        self.__write(self.LCD_CLEARDISPLAY)
        self.__write(self.LCD_RETURNHOME)

    def setBacklight(self, enabled: bool):
        """ If enabled, turns on the backlight, otherwise turns it off """
        if enabled:
            self.__backlightState = self.LCD_BACKLIGHT
            self.__write_cmd(self.LCD_BACKLIGHT)
            self.__write(self.LCD_CLEARDISPLAY)
            self.clear()
        else:
            self.__backlightState = self.LCD_NOBACKLIGHT
            self.__write_cmd(self.LCD_NOBACKLIGHT)

    def commit(self):
        """ Commits all pending changes to the display """
        results = super().commit()
        for i in range(len(results)):
            for change in results[i]:
                self.__write_str(change[0], i, change[1])


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


class Button(Enum):
    UP = 1
    DOWN = 2
    MODE = 3
    WAKE = 4


class ButtonPressedEvent(Event):
    def __init__(self, button: Button):
        super().__init__(data={'button': button})

    @property
    def button(self):
        return super().data['button']


class HardwareThermostatDriver(GenericThermostatDriver):

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        try:
            sensor = Bm280EnvironmentSensor()
        except:
            # Debugging w/o the bmp280 on the breadboard
            sensor = GenericEnvironmentSensor()

        super().__init__(
            lcd=HD44780Display(0x27, 20, 4),
            sensor=sensor,
            relays=(
                PanasonicAgqRelay(ThermostatState.FAN, 5, 17),
                PanasonicAgqRelay(ThermostatState.HEATING, 6, 27),
                PanasonicAgqRelay(ThermostatState.COOLING, 13, 22),
            )
        )

        super()._installEventHandler(
            ButtonPressedEvent, self.__buttonPressedHandler)

        self.__pinToButtonMap = {}
        self.__subscribeToButton(21, Button.UP)
        self.__subscribeToButton(20, Button.DOWN)
        self.__subscribeToButton(16, Button.MODE)
        self.__subscribeToButton(12, Button.WAKE)

        # print("Sleeping to watch buttons")
        # sleep(10)
        # print("DONE Sleeping to watch buttons")

    def __buttonPressedHandler(self, event: ButtonPressedEvent):
        if event.button == Button.UP:
            super()._modifyComfortSettings(1)
        elif event.button == Button.DOWN:
            super()._modifyComfortSettings(-1)
        elif event.button == Button.MODE:
            super()._rotateState()

    def __subscribeToButton(self, pin: int, button: Button):
        self.__pinToButtonMap[pin] = button

        GPIO.setup(
            pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(
            pin, GPIO.RISING, callback=self.__buttonCallback, bouncetime=200)

    def __buttonCallback(self, channel):
        button = self.__pinToButtonMap[channel]
        self._fireEvent(ButtonPressedEvent(button))
