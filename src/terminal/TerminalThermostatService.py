import curses

from queue import Queue
from threading import Thread

from .TerminalDisplay import TerminalDisplay
from .TerminalRelay import TerminalRelay
from src.logging import log
from src.generics import  \
    ThermostatDriver, GenericEnvironmentSensor, \
    PowerPriceChangedEvent, ThermostatState, \
    SensorDataChangedEvent
from src.core import EventBus, Event
from src.core import ServiceProvider


class TerminalThermostatService(ThermostatDriver):

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

        self.__lcd = TerminalDisplay(self.__displayWin, 20, 4)
        super().__init__(
            lcd=self.__lcd,
            sensor=self.__environmentSensor,
            relays=self.__relayList,
        )

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)
        super()._installEventHandler(
            TerminalThermostatService.KeyPressedEvent, self.__keyPressedHandler)
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
        self.__logWin.refresh()
        self.__lcd.refresh()

    def __keyPressedHandler(self, event: KeyPressedEvent):
        # Handle any key presses
        char = event.key
        if char == ord('l'):
            self.__stdscr.clear()
            self.__stdscr.refresh()
            self.__updateDisplay()
        elif char == ord('9'):
            super()._fireEvent(PowerPriceChangedEvent(
                price=self.__lastPrice-0.25, nextUpdate=1))
        elif char == ord('0'):
            super()._fireEvent(PowerPriceChangedEvent(
                price=self.__lastPrice+0.25, nextUpdate=1))
        elif char == ord('1'):
            if not super().relayToggled:
                super()._modifyComfortSettings(1)
        elif char == ord('2'):
            if not super().relayToggled:
                super()._modifyComfortSettings(-1)
        elif char == ord('3'):
            if not super().relayToggled:
                super()._nextMode()
            else:
                log.debug("Ignoring button during relay closure")
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
                    TerminalThermostatService.KeyPressedEvent(char))

        super()._getService(EventBus).stop()

    def __processMessageQueue(self):
        # Update any pending log messages to the log window
        if self.__messageQueue.qsize():
            self.__updateDisplay()
        while self.__messageQueue.qsize():
            message = self.__messageQueue.get()
            y, x = self.__logWin.getmaxyx()
            self.__logWin.scroll()
            self.__logWin.move(y-1, 0)
            self.__logWin.insnstr(message.getMessage(), x)
            self.__logWin.refresh()
