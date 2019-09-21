from src.logging import log
from src.settings import settings, Settings, SettingsChangedEvent
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

    def __init__(self, id: int):
        self.__id = id
        self.__isPressed = False

    @property
    def id(self):
        return self.__id

    def press(self):
        self.__isPressed = True

    def query(self):
        pressed = self.__isPressed
        self.__isPressed = False
        return pressed


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

    def __init__(self):
        super().__init__()
        self.__temperature = 72.0
        self.__pressure = 1015.0
        self.__humidity = 40.0

    @property
    def temperature(self):
        return self.__temperature

    @temperature.setter
    def temperature(self, value):
        self.__temperature = value

    @property
    def pressure(self):
        return 1015.0

    @pressure.setter
    def pressure(self, value):
        self.__pressure = value

    @property
    def humidity(self):
        return 40.0

    @humidity.setter
    def humidity(self, value):
        self.__humidity = value


class PowerPriceChangedEvent(Event):
    """ Signals the start of a new power price """

    def __init__(self, price: float):
        super().__init__(data={'price': price})

    @property
    def price(self):
        """ Returns the new power price in $/kW*h """
        return self._data['price']


class GenericScreen(EventHandler):

    def __init__(self,
                 width: int,
                 height: int,
                 eventBus: EventBus,
                 loopSleep: int):
        super().__init__(eventBus, loopSleep)
        self.__eventBus = eventBus
        self.__lcdBuffer = GenericLcdDisplay(width=width, height=height)

    def _fireEvent(self, event: Event):
        self.__eventBus.put(event)

    @property
    def lcdBuffer(self):
        return self.__lcdBuffer

    def processButton(self, button: GenericButton):
        raise NotImplementedError

    def drawLcdDisplay(self, display: GenericLcdDisplay):
        raise NotImplementedError


class DefaultScreen(GenericScreen):

    def __init__(self,
                 width: int,
                 height: int,
                 sensor: GenericEnvironmentSensor,
                 eventBus: EventBus,
                 loopSleep: int):
        super().__init__(width, height, eventBus, loopSleep)
        self.__sensor = sensor

        self.__lastTemperature = sensor.temperature
        self.__lastState = ThermostatState.OFF
        self.__lastPrice = 0.0

        self.__sampleInvoker = CounterBasedInvoker(
            ticks=max(1, int(5/loopSleep)), handlers=[self.__sampleSensors])
        self.__drawLcdInvoker = CounterBasedInvoker(
            ticks=max(1, int(0.1/loopSleep)), handlers=[self.__drawLcdDisplay])
        self.__drawRowTwoInvoker = CounterBasedInvoker(
            ticks=max(1, int(3/loopSleep)), handlers=[
                self.__drawRowTwoTarget,
                self.__drawRowTwoState,
                self.__drawRowTwoPrice])

        self.__rotateRowTwoInterval = int(3/loopSleep)

        super()._subscribe(
            SettingsChangedEvent, self.__processSettingsChanged)
        super()._subscribe(
            TemperatureChangedEvent, self.__processTemperatureChanged)
        super()._subscribe(
            ThermostatStateChangedEvent, self.__processStateChanged)
        super()._subscribe(
            PowerPriceChangedEvent, self.__powerPriceChanged)

        self.__sampleSensors()

    def processEvents(self):
        super().processEvents()

        # Update the LCD display with the current page's content
        self.__drawLcdInvoker.increment()
        self.__drawRowTwoInvoker.increment(execute=False)

        # Only update measurements at the sample interval
        self.__sampleInvoker.increment()

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        log.info(f"DefaultScreen: Power price is now {event.price:.4f}/kW*h")
        self.__drawRowTwoInvoker.reset(2)
        self.__lastPrice = event.price
        self.__drawLcdInvoker.invokeCurrent()

    def __processTemperatureChanged(self, event: TemperatureChangedEvent):
        self.__lastTemperature = event.value
        self.__drawLcdInvoker.invokeCurrent()

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        log.debug(f"DefaultScreen: new settings: {settings}")
        self.__drawLcdInvoker.invokeCurrent()

    def __processStateChanged(self, event: ThermostatStateChangedEvent):
        log.debug(f"DefaultScreen: new state: {event.state}")
        self.__lastState = event.state
        self.__drawLcdInvoker.reset()

    def __sampleSensors(self):
        super()._fireEvent(TemperatureChangedEvent(self.__sensor.temperature))
        super()._fireEvent(PressureChangedEvent(self.__sensor.pressure))
        super()._fireEvent(HumidityChangedEvent(self.__sensor.humidity))

    def processButton(self, button: GenericButton):
        log.debug(f"DefaultScreen.processBUtton saw button {button.id}")
        if 1 == button.id:
            self.__modifyComfortSettings(1)
        elif 2 == button.id:
            self.__modifyComfortSettings(-1)
        elif 3 == button.id:
            self.__drawRowTwoInvoker.reset(1)
            settings.mode = Settings.Mode(
                (int(settings.mode.value)+1) % len(Settings.Mode))
        elif 4 == button.id:
            self.__drawRowTwoInvoker.increment()

    def __modifyComfortSettings(self, increment: int):
        self.__drawRowTwoInvoker.reset(0)
        if Settings.Mode.HEAT == settings.mode:
            settings.comfortMin = \
                settings.comfortMin + increment
        if Settings.Mode.COOL == settings.mode:
            settings.comfortMax = \
                settings.comfortMax + increment

    def __drawRowTwoTarget(self):
        heat = settings.comfortMin
        cool = settings.comfortMax
        self.lcdBuffer.update(1, 0, f'Target:      {heat:<3.0f}/{cool:>3.0f}')

    def __drawRowTwoState(self):
        state = str(self.__lastState).replace('ThermostatState.', '')
        self.lcdBuffer.update(1, 0, f'State:     {state:>9s}')

    def __drawRowTwoPrice(self):
        price = self.__lastPrice
        self.lcdBuffer.update(1, 0, f'Price:  ${price:.4f}/kW*h')
        # '01234567890123456789'
        # 'Price:  $0.0356/kW*h'

    def __drawLcdDisplay(self):
        now = self.__lastTemperature
        mode = str(settings.mode).replace('Mode.', '')
        self.lcdBuffer.update(0, 0, f'Now: {now:<5.1f}    {mode:>6s}')
        self.lcdBuffer.update(3, 0, r'UP  DOWN  MODE  NEXT')
        self.__drawRowTwoInvoker.invokeCurrent()

    # 01234567890123456789
    # Now: ###.#      AUTO
    # Stat         COOLING
    #
    # UP  DOWN  MODE  NEXT


class GenericHardwareDriver(EventHandler):

    def __init__(self,
                 lcd: GenericLcdDisplay,
                 sensor: GenericEnvironmentSensor,
                 buttons: list,
                 eventBus: EventBus,
                 loopSleep: int=0.05):
        super().__init__(eventBus, loopSleep)

        self.__lcd = lcd
        self.__buttons = buttons
        self.__activeScreenIndex = 0
        self.__screens = [
            DefaultScreen(
                lcd.width, lcd.height, sensor, eventBus, loopSleep)
        ]

    def processEvents(self):
        super().processEvents()

        for screen in self.__screens:
            screen.processEvents()

        activeScreen = self.__screens[self.__activeScreenIndex]

        # Always scan for button presses
        for button in self.__buttons:
            if button.query():
                activeScreen.processButton(button)

        # Send buffered updates to the actual display
        activeScreen.lcdBuffer.commit()
        for row in range(self.__lcd.height):
            self.__lcd.update(
                row, 0, activeScreen.lcdBuffer.rowText(row))
        self.__lcd.commit()
