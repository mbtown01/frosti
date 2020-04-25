import curses

from queue import Queue
from threading import Thread

from .TerminalDisplay import TerminalDisplay
from .TerminalRgbLed import TerminalRgbLed
from .TerminalRedrawEvent import TerminalRedrawEvent

from src.core.events import  \
    PowerPriceChangedEvent, SensorDataChangedEvent, \
    UserThermostatInteractionEvent
from src.core import EventBus, Event, ServiceProvider
from src.core.generics import GenericEnvironmentSensor, GenericRgbLed, \
    GenericUserInterface


class TerminalKeyPressedEvent(Event):
    def __init__(self, key):
        super().__init__(name='TerminalKeyPressedEvent', data={'key': key})

    @property
    def key(self):
        return super().data['key']


class TerminalUserInterface(GenericUserInterface):

    def __init__(
            self, stdscr,
            sensor: GenericEnvironmentSensor,
            messageQueue: Queue):
        self.__stdscr = stdscr
        self.__messageQueue = messageQueue
        self.__logWinMessages = []
        self.__environmentSensor = sensor
        self.__stdscr.clear()
        self.__lastPrice = 0.0

        curses.noecho()
        curses.cbreak()
        curses.setupterm()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.curs_set(0)

        self.__displayWin = curses.newwin(4, 21, 0, 5)
        self.__leftLed = TerminalRgbLed(curses.newwin(2, 3, 1, 1))
        self.__leftLed.setColor(GenericRgbLed.Color.RED)
        self.__rightLed = TerminalRgbLed(curses.newwin(2, 3, 1, 6 + 20))
        self.__rightLed.setColor(GenericRgbLed.Color.BLUE)
        self.__instructionsWin = curses.newwin(7, 30, 0, 50)

        lines, cols = self.__stdscr.getmaxyx()
        self.__logWin = curses.newwin(lines - 5, cols, 5, 0)
        self.__logWin.scrollok(True)

        self.__lcd = TerminalDisplay(self.__displayWin, 7, 20, 4)
        super().__init__(
            lcd=self.__lcd,
            rgbLeds=[self.__leftLed, self.__rightLed]
        )

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)
        super()._installEventHandler(
            TerminalKeyPressedEvent, self.__terminalKeyPressed)
        super()._installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)

        super()._installTimerHandler(
            frequency=1.0, handlers=self.__processMessageQueue)

        self.__keyPressThread = Thread(
            target=self.__keyPressListener,
            name='Terminal Keypress Listener',
            daemon=True)
        self.__keyPressThread.start()

        self.__updateDisplay()

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        self.__lastPrice = event.price

    def __updateDisplay(self):
        super()._fireEvent(TerminalRedrawEvent())

        self.__lcd.refresh()
        self.__updateInstructions()
        self.__updateLogWin()

    def __updateInstructions(self):
        self.__instructionsWin.clear()
        self.__instructionsWin.addstr(
            0, 0, '1-4: Buttons on thermostat  ',
            curses.A_REVERSE | curses.color_pair(7))
        self.__instructionsWin.addstr(
            1, 0, '9,0: Simulate price movement',
            curses.A_REVERSE | curses.color_pair(7))
        self.__instructionsWin.addstr(
            2, 0, 'Up/Dwn arrows: Change temp  ',
            curses.A_REVERSE | curses.color_pair(7))
        self.__instructionsWin.addstr(
            3, 0, 'q: quit, l: redraw screen   ',
            curses.A_REVERSE | curses.color_pair(7))
        self.__instructionsWin.refresh()

    def __updateLogWin(self):
        self.__logWin.clear()
        y, x = self.__logWin.getmaxyx()
        self.__logWin.clear()
        for message in self.__logWinMessages:
            self.__logWin.scroll()
            self.__logWin.move(y - 1, 0)
            self.__logWin.insnstr(message, x)

        self.__logWin.refresh()
        self.__logWinMessages = self.__logWinMessages[-y:]

    def __terminalKeyPressed(self, event: TerminalKeyPressedEvent):
        # Handle any key presses
        char = event.key
        if char == ord('l'):
            self.__stdscr.clear()
            self.__stdscr.refresh()
            self.__updateDisplay()
        elif char == ord('9'):
            super()._fireEvent(PowerPriceChangedEvent(
                price=self.__lastPrice - 0.25, nextUpdate=1))
        elif char == ord('0'):
            super()._fireEvent(PowerPriceChangedEvent(
                price=self.__lastPrice + 0.25, nextUpdate=1))
        elif char == ord('1'):
            super().backlightReset()
            self._fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.COMFORT_RAISE))
        elif char == ord('2'):
            super().backlightReset()
            self._fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.COMFORT_LOWER))
        elif char == ord('3'):
            super().backlightReset()
            self._fireEvent(UserThermostatInteractionEvent(
                UserThermostatInteractionEvent.MODE_NEXT))
        elif char == ord('4'):
            super().backlightReset()
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
        """ Marshalls an incoming threaded keypress to the main event loop """
        char = None
        while char != ord('q'):
            char = self.__stdscr.getch()
            if char >= 0:
                super()._fireEvent(TerminalKeyPressedEvent(char))

        super()._getService(EventBus).stop()

    def __processMessageQueue(self):
        needsUpdate = self.__messageQueue.qsize()
        while self.__messageQueue.qsize():
            message = self.__messageQueue.get()
            self.__logWinMessages.append(message.getMessage())

        if needsUpdate:
            self.__updateLogWin()
