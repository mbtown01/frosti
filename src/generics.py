from enum import Enum

from src.logging import log
from src.settings import Settings, SettingsChangedEvent
from src.events import EventBus, EventHandler, Event
from src.thermostat import ThermostatState, ThermostatStateChangedEvent, \
    PressureChangedEvent, HumidityChangedEvent, TemperatureChangedEvent


class GenericLcdDisplay:
    """ Generic implementation of a multi-line LCD with a cursor-based
    interface """

    class Row:
        """ A row of text on a generic cursor-based LCD display """

        def __init__(self, width: int):
            self.__width = width
            self.clear()

        @property
        def text(self):
            return ''.join(self.__buffer)

        def clear(self):
            self.__buffer = list()
            self.__updates = list()
            for _ in range(self.__width):
                self.__buffer.append(' ')
                self.__updates.append(' ')

        def update(self, offset: int, text: str):
            """ Write 'text' at the specified offset on the row """
            if offset < 0:
                text = text[abs(offset):]
                offset = 0
            for i in range(min(self.__width-offset, len(text))):
                self.__updates[i+offset] = text[i]

        def commit(self):
            """ Commit all pending updates and build a list of changes """
            results = list()
            offset = 0
            while offset < self.__width:
                change = list()
                while offset+len(change) < self.__width and \
                        self.__updates[offset+len(change)] != \
                        self.__buffer[offset+len(change)]:
                    self.__buffer[offset+len(change)] = \
                        self.__updates[offset+len(change)]
                    change.append(self.__updates[offset+len(change)])
                if len(change):
                    results.append([offset, ''.join(change)])
                offset += len(change) + 1

            return results

    def __init__(self, width: int, height: int):
        self.__rows = list()
        self.__width = width
        self.__height = height

        for _ in range(height):
            self.__rows.append(GenericLcdDisplay.Row(width))

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def text(self):
        rowText = list()
        for row in self.__rows:
            rowText.append(row.text)
        return '\n'.join(rowText)

    def rowText(self, row: int):
        return self.__rows[row].text

    def clear(self):
        """ Clear all rows and pending updates """
        for row in self.__rows:
            row.clear()

    def update(self, row: int, col: int, text: str):
        """ Add a pending change to the display """
        if row >= len(self.__rows):
            raise RuntimeError(
                f"Row {row} is out of range, max={len(self.__rows)-1}")
        self.__rows[row].update(col, text)

    def commit(self):
        """ Commit the set of pending changes and return the changes from
        the previous compit """
        results = list()
        for row in self.__rows:
            results.append(row.commit())

        return results


class GenericButton:
    """ A logical button provided to the user """

    class Action(Enum):
        MODE = 1
        UP = 2
        DOWN = 3
        ENTER = 4

    def __init__(self, action: Action):
        self.__action = action

    @property
    def action(self):
        return self.__action

    def query(self):
        raise NotImplementedError()


class CounterBasedInvoker:
    """ Invokes a handler based on a set number of ticks """

    def __init__(self, ticks: int, handlers: list):
        """ Creates a new CounterBasedInvoker

        ticks: int
            Number of calls to increment it takes to invoke the handler
        handlers: list
            List of handlers, called in sequential/rotating order
        """
        self.__ticks = ticks
        self.__handlers = handlers
        self.__lastHandler = 0
        self.__counter = 0

    def increment(self, execute=True):
        """ Increments the counter and executes the next handler if it is
        a harmonic of ticks

        execute: bool
            True if increment should execute the counter, false otherwise
        """
        self.__counter += 1
        if 0 == self.__counter % self.__ticks:
            if execute:
                self.invokeCurrent()
            self.__lastHandler = \
                (self.__lastHandler + 1) % len(self.__handlers)

    def invokeCurrent(self):
        """ Force an invoke of the current handler, does not increment the
        counter """
        self.__handlers[self.__lastHandler]()

    def reset(self, handler: int=None):
        """ Resets the counter to zero and the next handler to be the first
        in the list """
        self.__lastHandler = handler or 0
        self.__counter = 1


class GenericEnvironmentSensor:

    @property
    def temperature(self):
        raise NotImplementedError()

    @property
    def pressure(self):
        raise NotImplementedError()

    @property
    def humidity(self):
        raise NotImplementedError()


class GenericHardwareDriver(EventHandler):

    def __init__(self,
                 lcd: GenericLcdDisplay,
                 sensor: GenericEnvironmentSensor,
                 buttons: list,
                 eventBus: EventBus,
                 loopSleep: int=0.05):
        self.__lcd = lcd
        self.__buttons = buttons
        self.__sensor = sensor

        self.__settings = Settings()
        self.__lastTemperature = 0
        self.__lastHumidity = 0
        self.__lastPressure = 0
        self.__lastState = ThermostatState.OFF

        self.__sampleInvoker = CounterBasedInvoker(
            ticks=max(1, int(5/loopSleep)), handlers=[self.__sampleSensors])
        self.__drawLcdInvoker = CounterBasedInvoker(
            ticks=max(1, int(0.1/loopSleep)), handlers=[self.__drawLcdDisplay])
        self.__drawRowTwoInvoker = CounterBasedInvoker(
            ticks=max(1, int(3/loopSleep)), handlers=[
                self.__drawRowTwoTarget, self.__drawRowTwoState])

        self.__rotateRowTwoInterval = int(3/loopSleep)
        self.__buttonHandler = self.__buttonHandlerDefault

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

    def _processStateChanged(self, event: ThermostatStateChangedEvent):
        pass

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        log.debug(f"HardwareDriver: new settings: {event.settings}")
        self.__settings = event.settings

    def __processStateChanged(self, event: ThermostatStateChangedEvent):
        log.debug(f"HardwareDriver: new state: {event.state}")
        self.__lastState = event.state
        self.__drawLcdInvoker.reset()
        self._processStateChanged(event)

    def __sampleSensors(self):
        self.__lastTemperature = self.__sensor.temperature
        self.__lastPressure = self.__sensor.pressure
        self.__lastHumidity = self.__sensor.humidity
        super()._fireEvent(TemperatureChangedEvent(self.__lastTemperature))
        super()._fireEvent(PressureChangedEvent(self.__lastPressure))
        super()._fireEvent(HumidityChangedEvent(self.__lastHumidity))

    def __buttonHandlerDefault(self, button: GenericButton):
        log.debug(f"DefaultButtonHandler saw {button.action}")
        if GenericButton.Action.MODE == button.action:
            self.__drawRowTwoInvoker.reset(1)
            self.__settings = self.__settings.clone(mode=Settings.Mode(
                (int(self.__settings.mode.value)+1) % len(Settings.Mode)))
            super()._fireEvent(SettingsChangedEvent(self.__settings))
        elif GenericButton.Action.UP == button.action:
            self.__modifyComfortSettings(1)
        elif GenericButton.Action.DOWN == button.action:
            self.__modifyComfortSettings(-1)

    def __modifyComfortSettings(self, increment: int):
        self.__drawRowTwoInvoker.reset(0)
        if Settings.Mode.HEAT == self.__settings.mode:
            self.__settings = self.__settings.clone(
                comfortMin=self.__settings.comfortMin + increment)
            super()._fireEvent(SettingsChangedEvent(self.__settings))
        if Settings.Mode.COOL == self.__settings.mode:
            self.__settings = self.__settings.clone(
                comfortMax=self.__settings.comfortMax + increment)
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
