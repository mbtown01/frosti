import curses

from queue import Queue

from src.logging import log
from src.generics import GenericLcdDisplay, GenericButton, \
    GenericHardwareDriver, GenericEnvironmentSensor, \
    PowerPriceChangedEvent
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
        for row in range(self.height):
            self.__window.addstr(row, 0, super().rowText(row))
        self.__window.refresh()


class TerminalHardwareDriver(GenericHardwareDriver):

    def __init__(self, stdscr, messageQueue: Queue, eventBus: EventBus):
        self.__stdscr = stdscr
        self.__messageQueue = messageQueue
        self.__environmentSensor = GenericEnvironmentSensor()
        self.__stdscr.nodelay(True)
        self.__stdscr.clear()
        self.__lastPrice = 0.0

        curses.noecho()
        curses.cbreak()
        curses.setupterm()
        curses.curs_set(0)

        lines, cols = self.__stdscr.getmaxyx()
        self.__displayWin = curses.newwin(4, cols, 0, 0)
        self.__logWin = curses.newwin(lines-5, cols, 5, 0)
        self.__logWin.scrollok(True)
        self.__buttonMap = {
            ord('1'): GenericButton(1),
            ord('2'): GenericButton(2),
            ord('3'): GenericButton(3),
            ord('4'): GenericButton(4),
        }

        super().__init__(
            eventBus=eventBus,
            loopSleep=0.1,
            lcd=TerminalDisplay(self.__displayWin, 20, 4),
            sensor=self.__environmentSensor,
            buttons=self.__buttonMap.values(),
        )

        super()._subscribe( 
            PowerPriceChangedEvent, self.__powerPriceChanged )

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        log.info(f"TerminalDriver: Power price is now {event.price:.4f}/kW*h")
        self.__lastPrice = event.price

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
            elif char == ord('9'):
                super()._fireEvent(PowerPriceChangedEvent(self.__lastPrice-0.25))
            elif char == ord('0'):
                super()._fireEvent(PowerPriceChangedEvent(self.__lastPrice+0.25))
            elif char in self.__buttonMap:
                self.__buttonMap[char].press()
            elif char == curses.KEY_UP:
                self.__environmentSensor.temperature += 1
                self._fireEvent(TemperatureChangedEvent(
                    self.__environmentSensor.temperature))
            elif char == curses.KEY_DOWN:
                self.__environmentSensor.temperature -= 1
                self._fireEvent(TemperatureChangedEvent(
                    self.__environmentSensor.temperature))
            elif char == curses.KEY_RESIZE:
                y, x = self.__logWin.getmaxyx()
                self.__logWin.resize(y, x)
