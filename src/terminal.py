import sys
import os
import termios
import fcntl
import select

from queue import Queue
from time import sleep

from src.logging import log
from src.generics import GenericLcdDisplay, GenericButton, \
    CounterBasedInvoker, GenericHardwareDriver, GenericEnvironmentSensor
from src.settings import Settings, SettingsChangedEvent
from src.events import EventBus, EventHandler, Event
from src.thermostat import ThermostatStateChangedEvent, ThermostatState, \
    TemperatureChangedEvent, PressureChangedEvent, HumidityChangedEvent


class TerminalDisplay(GenericLcdDisplay):

    # Modified version of the driver from
    # https://github.com/sunfounder/SunFounder_SensorKit_for_RPi2.git
    def __init__(self, addr, width, height):
        super().__init__(width, height)

    def commit(self):
        """ Commits all pending changes to the display """
        super().commit()
        print(f"\n\n{super().text}")


class TerminalButton(GenericButton):
    """ A physical button provided to the user """

    def __init__(self, action: GenericButton.Action):
        super().__init__(action)
        self.__isPressed = False

    def press(self):
        self.__isPressed = True

    def query(self):
        pressed = self.__isPressed
        self.__isPressed = False
        return pressed


class TerminalEnvironmentSensor(GenericEnvironmentSensor):

    def __init__(self):
        super().__init__()

    @property
    def temperature(self):
        return 72.0

    @property
    def pressure(self):
        return 1015.0

    @property
    def humidity(self):
        return 40.0


class TerminalHardwareDriver(GenericHardwareDriver):

    def __init__(self, eventBus: EventBus):
        fd = sys.stdin.fileno()
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON
        newattr[3] = newattr[3] & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        # oldterm = termios.tcgetattr(fd)
        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        self.__buttonMap = {
            'k': TerminalButton(GenericButton.Action.UP),
            'j': TerminalButton(GenericButton.Action.DOWN),
            '\n': TerminalButton(GenericButton.Action.ENTER),
            '\t': TerminalButton(GenericButton.Action.MODE),
        }

        super().__init__(
            eventBus=eventBus,
            loopSleep=0.25,
            lcd=TerminalDisplay(0x27, 16, 2),
            sensor=TerminalEnvironmentSensor(),
            buttons=self.__buttonMap.values(),
        )

    def processEvents(self):
        super().processEvents()

        foo, _, _ = select.select([sys.stdin], [], [], 0)
        if len(foo):
            chars = sys.stdin.read()
            for i in range(len(chars)):
                if chars[i] in self.__buttonMap:
                    self.__buttonMap[chars[i]].press()
