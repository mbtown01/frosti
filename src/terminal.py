import curses

from queue import Queue
from threading import Thread

from src.logging import log
from src.generics import GenericLcdDisplay, \
    GenericThermostatDriver, GenericEnvironmentSensor, \
    PowerPriceChangedEvent, GenericRelay, ThermostatState, \
    SensorDataChangedEvent
from src.events import EventBus, Event, TimerBasedHandler
from src.services import ServiceProvider


class TerminalDisplay(GenericLcdDisplay):

    # Modified version of the driver from
    # https://github.com/sunfounder/SunFounder_SensorKit_for_RPi2.git
    def __init__(self, window, width, height):
        super().__init__(width, height)
        self.__window = window
        self.__backlightEnabled = False

    def setBacklight(self, enabled: bool):
        self.__backlightEnabled = enabled
        self.commit()

    def commit(self):
        """ Commits all pending changes to the display """
        results = super().commit()
        filtered = [l for l in results if len(l)]
        if len(filtered):
            for row in range(self.height):
                if self.__backlightEnabled:
                    self.__window.addstr(
                        row, 0, super().rowText(row), curses.A_REVERSE)
                else:
                    self.__window.addstr(
                        row, 0, super().rowText(row))
            self.__window.refresh()


class TerminalRelay(GenericRelay):

    def __init__(self, function: ThermostatState,
                 colorPair: int, row: int, col: int):
        super().__init__(function)

        self.__displayWin = curses.newwin(1, 16, row, col)
        self.__isClosed = None
        self.__colorPair = curses.color_pair(colorPair)

    def redraw(self):
        self.__displayWin.clear()
        if self.__isClosed is None:
            self.__displayWin.addstr(
                0, 0, self.function.name + ' UNKNOWN')
        elif self.__isClosed:
            self.__displayWin.addstr(
                0, 0, self.function.name + ' CLOSED',
                curses.A_REVERSE | self.__colorPair)
        else:
            self.__displayWin.addstr(
                0, 0, self.function.name + ' OPEN')

        self.__displayWin.refresh()

    def openRelay(self):
        self.__isClosed = False
        self.redraw()

    def closeRelay(self):
        self.__isClosed = True
        self.redraw()


class TerminalThermostatDriver(GenericThermostatDriver):

    class KeyPressedEvent(Event):
        def __init__(self, key):
            super().__init__(name='KeyPressedEvent', data={'key': key})

        @property
        def key(self):
            return super().data['key']

    def __init__(self, stdscr, messageQueue: Queue):
        self.__stdscr = stdscr
        self.__messageQueue = messageQueue
        self.__environmentSensor = GenericEnvironmentSensor()
        # self.__stdscr.nodelay(True)
        self.__stdscr.clear()
        self.__lastPrice = 0.0

        curses.noecho()
        curses.cbreak()
        curses.setupterm()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.curs_set(0)

        lines, cols = self.__stdscr.getmaxyx()
        self.__displayWin = curses.newwin(4, cols, 0, 0)
        self.__logWin = curses.newwin(lines-5, cols, 5, 0)
        self.__logWin.scrollok(True)
        self.__relayList = (
            TerminalRelay(ThermostatState.HEATING, 1, 0, 32),
            TerminalRelay(ThermostatState.COOLING, 2, 1, 32),
            TerminalRelay(ThermostatState.FAN, 3, 2, 32),
        )

        super().__init__(
            lcd=TerminalDisplay(self.__displayWin, 20, 4),
            sensor=self.__environmentSensor,
            relays=self.__relayList,
        )

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)
        super()._installEventHandler(
            TerminalThermostatDriver.KeyPressedEvent, self.__keyPressedHandler)
        super()._installTimerHandler(
            frequency=5.0, handlers=self.__updateDisplay)
        super()._installTimerHandler(
            frequency=1.0, handlers=self.__processMessageQueue)

        self.__keyPressThread = Thread(
            target=self.__keyPressListener,
            name='Terminal Keypress Listener',
            daemon=True)
        self.__keyPressThread.start()

    def _powerPriceChanged(self, event: PowerPriceChangedEvent):
        super()._powerPriceChanged(event)
        self.__lastPrice = event.price

    def __updateDisplay(self):
        # Redraw the relay status
        for relay in self.__relayList:
            relay.redraw()

    def __keyPressedHandler(self, event: KeyPressedEvent):
        # Handle any key presses
        char = event.key
        if char == ord('l'):
            self.__stdscr.clear()
            self.__stdscr.refresh()
        elif char == ord('9'):
            super()._fireEvent(PowerPriceChangedEvent(
                price=self.__lastPrice-0.25, nextUpdate=1))
        elif char == ord('0'):
            super()._fireEvent(PowerPriceChangedEvent(
                price=self.__lastPrice+0.25, nextUpdate=1))
        elif char == ord('1'):
            super()._modifyComfortSettings(1)
        elif char == ord('2'):
            super()._modifyComfortSettings(-1)
        elif char == ord('3'):
            super()._nextMode()
        elif char == curses.KEY_UP:
            self.__environmentSensor.temperature += 1
            self._fireEvent(SensorDataChangedEvent(
                temperature=self.__environmentSensor.temperature,
                pressure=self.__environmentSensor.pressure,
                humidity=self.__environmentSensor.humidity))
        elif char == curses.KEY_DOWN:
            self.__environmentSensor.temperature -= 1
            self._fireEvent(SensorDataChangedEvent(
                temperature=self.__environmentSensor.temperature,
                pressure=self.__environmentSensor.pressure,
                humidity=self.__environmentSensor.humidity))
        elif char == curses.KEY_RESIZE:
            y, x = self.__logWin.getmaxyx()
            self.__logWin.resize(y, x)

    def __keyPressListener(self):
        char = None
        while char != ord('q'):
            char = self.__stdscr.getch()
            if char >= 0:
                super()._fireEvent(
                    TerminalThermostatDriver.KeyPressedEvent(char))

        super()._getService(EventBus).stop()

    def __processMessageQueue(self):
        # Update any pending log messages to the log window
        while self.__messageQueue.qsize():
            message = self.__messageQueue.get()
            y, x = self.__logWin.getmaxyx()
            self.__logWin.scroll()
            self.__logWin.move(y-1, 0)
            self.__logWin.insnstr(message.getMessage(), x)
            self.__logWin.refresh()
