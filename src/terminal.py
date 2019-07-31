import curses

from queue import Queue

from src.logging import log
from src.generics import GenericLcdDisplay, GenericButton, \
    GenericHardwareDriver, GenericEnvironmentSensor
from src.events import EventBus
from src.thermostat import TemperatureChangedEvent


class TerminalDisplay(GenericLcdDisplay):

    # Modified version of the driver from
    # https://github.com/sunfounder/SunFounder_SensorKit_for_RPi2.git
    def __init__(self, window, width, height):
        super().__init__(width, height)
        self.__window = window

    def commit(self):
        """ Commits all pending changes to the display """
        super().commit()
        self.__window.addstr(0, 0, super().rowText(0))
        self.__window.addstr(1, 0, super().rowText(1))
        self.__window.refresh()


class TerminalHardwareDriver(GenericHardwareDriver):

    def __init__(self, stdscr, messageQueue: Queue, eventBus: EventBus):
        self.__stdscr = stdscr
        self.__messageQueue = messageQueue
        self.__environmentSensor = GenericEnvironmentSensor()
        self.__stdscr.nodelay(True)
        self.__stdscr.clear()

        curses.noecho()
        curses.cbreak()
        curses.setupterm()
        curses.curs_set(0)

        lines, cols = self.__stdscr.getmaxyx()
        self.__displayWin = curses.newwin(2, cols, 0, 0)
        self.__logWin = curses.newwin(lines-3, cols, 3, 0)
        self.__logWin.scrollok(True)
        self.__buttonMap = {
            ord('k'): GenericButton(GenericButton.Action.UP),
            ord('j'): GenericButton(GenericButton.Action.DOWN),
            ord('\n'): GenericButton(GenericButton.Action.ENTER),
            ord('\t'): GenericButton(GenericButton.Action.MODE),
        }

        super().__init__(
            eventBus=eventBus,
            loopSleep=0.1,
            lcd=TerminalDisplay(self.__displayWin, 16, 2),
            sensor=self.__environmentSensor,
            buttons=self.__buttonMap.values(),
        )

    def processEvents(self):
        super().processEvents()

        # Update any pending log messages to the log window
        while self.__messageQueue.qsize():
            message = self.__messageQueue.get()
            y, x = self.__logWin.getmaxyx()
            self.__logWin.scroll()
            self.__logWin.move(y-1, 0)
            self.__logWin.insnstr(message.getMessage(), x)
            self.__logWin.refresh()

        # Handle any key presses
        char = self.__stdscr.getch()
        if char >= 0:
            if char == ord('l'):
                self.__stdscr.clear()
                self.__stdscr.refresh()
            if char in self.__buttonMap:
                self.__buttonMap[char].press()
            if char == curses.KEY_UP:
                self.__environmentSensor.temperature += 1
                self._fireEvent(TemperatureChangedEvent(
                    self.__environmentSensor.temperature))
            if char == curses.KEY_DOWN:
                self.__environmentSensor.temperature -= 1
                self._fireEvent(TemperatureChangedEvent(
                    self.__environmentSensor.temperature))
            if char == curses.KEY_RESIZE:
                y, x = self.__logWin.getmaxyx()
                self.__logWin.resize(y, x)
