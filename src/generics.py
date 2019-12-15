from enum import Enum
from time import time, localtime
import atexit

from src.logging import log
from src.settings import Settings, SettingsChangedEvent
from src.events import EventBus, EventBusMember, Event, TimerBasedHandler
from src.config import Config
from src.services import ServiceProvider


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

    def setBacklight(self, enabled: bool):
        pass

    def update(self, row: int, col: int, text: str):
        """ Add a pending change to the display """
        if row >= len(self.__rows):
            raise RuntimeError(
                f"Row {row} is out of range, max={len(self.__rows)-1}")
        self.__rows[row].update(col, text)

    def commit(self):
        """ Commit the set of pending changes and return the changes from
        the previous commit """
        results = list()
        for row in self.__rows:
            results.append(row.commit())

        return results


class GenericEnvironmentSensor:

    def __init__(self):
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


class ThermostatState(Enum):
    """ Represents the state the thermostat is in now.

    This should not be confused with mode, as mode is what the user has
    asked the thermostat to target (e.g. HEAT).  The mode could be HEAT but
    the state could be OFF """
    OFF = 0
    COOLING = 1
    HEATING = 2
    FAN = 3

    @property
    def shouldAlsoRunFan(self):
        """ Returns true if this state implies the use of the fan """
        return self == ThermostatState.HEATING or \
            self == ThermostatState.COOLING


class ThermostatStateChangedEvent(Event):
    def __init__(self, value: ThermostatState):
        super().__init__('ThermostatStateChangedEvent', {'state': value})

    @property
    def state(self):
        """ Returns the new state of the thermostat """
        return self._data['state']


class PropertyChangedEvent(Event):
    def __init__(self, name: str, value: float):
        super().__init__(name, {'value': value})

    @property
    def value(self):
        return float(self._data['value'])


class SensorDataChangedEvent(Event):
    def __init__(self, temperature: float, pressure: float, humidity: float):
        super().__init__(data={
            'temperature': temperature,
            'pressure': pressure,
            'humidity': humidity
        })

    @property
    def temperature(self):
        return float(self._data['temperature'])

    @property
    def pressure(self):
        return float(self._data['pressure'])

    @property
    def humidity(self):
        return float(self._data['humidity'])


class PowerPriceChangedEvent(Event):
    """ Signals the start of a new power price in $/kW*h """
    def __init__(self, price: float, nextUpdate: float):
        super().__init__(
            name='PowerPriceChangedEvent',
            data={'price': price, 'nextUpdate': nextUpdate})

    @property
    def price(self):
        """ Current price """
        return super().data['price']

    @property
    def nextUpdate(self):
        """ Seconds between this event and next price update """
        return super().data['nextUpdate']


class GenericRelay:

    def __init__(self, function: ThermostatState):
        self.__function = function
        self.__isOpen = None
        self.__callbackList = []

    @property
    def isOpen(self):
        """  True if open, False if closed, None if indeterminite """
        return self.__isOpen

    @property
    def function(self):
        """ Gets the ThermostatState function this relay handles """
        return self.__function

    def addCallback(self, callback):
        """ Provide a callback in the form of callback(relay: GenericRelay) to
        notify when the relay is opening or closing """
        self.__callbackList.append(callback)

    def openRelay(self):
        """ Open the relay, break circuit, disabling the function """
        for callback in self.__callbackList:
            callback(self)
        self._openRelay()
        self.__isOpen = True

    def closeRelay(self):
        """ Close the relay, connect circuit, enabling the function """
        for callback in self.__callbackList:
            callback(self)
        self._closeRelay()
        self.__isOpen = False

    def _openRelay(self):
        pass

    def _closeRelay(self):
        pass


class UserThermostatInteractionEvent(Event):
    MODE_NEXT = 1
    COMFORT_RAISE = 2
    COMFORT_LOWER = 3

    def __init__(self, interaction: int):
        super().__init__(
            name='UserThermostatInteractionEvent',
            data={'interaction': interaction})

    @property
    def interaction(self):
        return super().data['interaction']


class GenericThermostatDriver(EventBusMember):

    def __init__(self,
                 lcd: GenericLcdDisplay,
                 sensor: GenericEnvironmentSensor,
                 relays: list):
        self.__lcd = lcd
        self.__sensor = sensor
        self.__relayToggled = False
        self.__relayMap = {r.function: r for r in relays}
        for relay in relays:
            relay.addCallback(self.__relayCallback)
        if ThermostatState.OFF not in self.__relayMap:
            self.__relayMap[ThermostatState.OFF] = \
                GenericRelay(ThermostatState.OFF)
        self.__state = ThermostatState.OFF
        self.__lcd.setBacklight(True)
        self.__lastTemperature = 0.0
        self.__lastState = ThermostatState.OFF
        self.__lastPrice = 0.0
        self.__fanRunoutInvoker = None

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        config = self._getService(Config)
        self.__delta = \
            config.value('thermostat').value('delta', 1.0)
        self.__fanRunoutDuration = \
            config.value('thermostat').value('fanRunout', 30)
        self.__backlightTimeoutDuration = \
            config.value('thermostat').value('backlightTimeout', 10)

        self.__sampleSensorsInvoker = self._installTimerHandler(
            frequency=5.0,
            handlers=self.__sampleSensors)
        self.__checkScheduleInvoker = self._installTimerHandler(
            frequency=60.0,
            handlers=self.__checkSchedule)
        self.__backlightTimeoutInvoker = self._installTimerHandler(
            frequency=self.__backlightTimeoutDuration,
            handlers=self.__backlightTimeout,
            oneShot=True)
        self.__relayToggledTimeoutInvoker = self._installTimerHandler(
            frequency=3.0, handlers=self.__relayToggledTimeout,
            oneShot=True)
        self.__drawRowTwoInvoker = self._installTimerHandler(
            frequency=3.0,
            handlers=[
                self.__drawRowTwoTarget,
                self.__drawRowTwoState,
                self.__drawRowTwoPrice,
                self.__drawRowTwoProgram])
        self.__fanRunoutInvoker = self._installTimerHandler(
            frequency=self.__fanRunoutDuration,
            handlers=self.__fanRunout,
            oneShot=True)
        self.__fanRunoutInvoker.disable()

        self._installEventHandler(
            SettingsChangedEvent, self.__processSettingsChanged)
        self._installEventHandler(
            SensorDataChangedEvent, self.__processSensorDataChanged)
        self._installEventHandler(
            ThermostatStateChangedEvent, self.__processStateChanged)
        self._installEventHandler(
            PowerPriceChangedEvent, self._powerPriceChanged)
        self._installEventHandler(
            UserThermostatInteractionEvent, self.__userThermostatInteraction)

        self.__lcd.setBacklight(True)
        self.__openAllRelays()
        self.__checkSchedule()

    @property
    def state(self):
        """ Current state of the thermostat """
        return self.__state

    @property
    def relayToggled(self):
        return self.__relayToggled

    def __checkSchedule(self):
        settings = self._getService(Settings)
        eventBus = self._getService(EventBus)

        if eventBus.now is None:
            raise RuntimeError("No time on eventBus")
        values = localtime(eventBus.now)
        settings.timeChanged(
            day=values.tm_wday, hour=values.tm_hour, minute=values.tm_min)
        # self.__sampleSensors()

    def __sampleSensors(self):
        temperature = self.__sensor.temperature
        settings = self._getService(Settings)
        super()._fireEvent(SensorDataChangedEvent(
            temperature=temperature,
            pressure=self.__sensor.pressure,
            humidity=self.__sensor.humidity
        ))

        #    HEATING ZONE         COMFORT ZONE           COOLING ZONE
        # \\\\\\\\\\\\\\\\\\\                        ///////////////////
        # --------(----+----)------------------------(----+----)--------
        #        h1    H    h2                      c2    C    c1
        c1 = settings.comfortMax+self.__delta
        c2 = settings.comfortMax-self.__delta
        h2 = settings.comfortMin+self.__delta
        h1 = settings.comfortMin-self.__delta

        modeOff = Settings.Mode.OFF == settings.mode
        modeFan = Settings.Mode.FAN == settings.mode
        modeHeat = Settings.Mode.HEAT == settings.mode
        modeCool = Settings.Mode.COOL == settings.mode
        modeAuto = Settings.Mode.AUTO == settings.mode
        couldHeat = modeAuto or modeHeat
        couldCool = modeAuto or modeCool

        if ThermostatState.OFF == self.__state:
            if couldHeat and temperature < h1:
                self.__changeState(ThermostatState.HEATING)
            elif couldCool and temperature > c1:
                self.__changeState(ThermostatState.COOLING)
            elif Settings.Mode.FAN == settings.mode:
                self.__changeState(ThermostatState.FAN)
        elif ThermostatState.HEATING == self.__state:
            if modeAuto and temperature > c1:
                self.__changeState(ThermostatState.COOLING)
            elif modeFan:
                self.__changeState(ThermostatState.FAN)
            elif modeOff:
                self.__changeState(ThermostatState.FAN)
                self.__fanRunoutInvoker.reset()
            elif (couldHeat and temperature > h2):
                self.__changeState(ThermostatState.FAN)
                self.__fanRunoutInvoker.reset()
            elif (modeCool and temperature < c2):
                self.__changeState(ThermostatState.FAN)
                self.__fanRunoutInvoker.reset()
        elif ThermostatState.COOLING == self.__state:
            if modeAuto and temperature < h1:
                self.__changeState(ThermostatState.HEATING)
            elif modeFan:
                self.__changeState(ThermostatState.FAN)
            elif modeOff:
                self.__changeState(ThermostatState.FAN)
                self.__fanRunoutInvoker.reset()
            elif (couldCool and temperature < c2):
                self.__changeState(ThermostatState.FAN)
                self.__fanRunoutInvoker.reset()
            elif (modeHeat and temperature > h2):
                self.__changeState(ThermostatState.FAN)
                self.__fanRunoutInvoker.reset()
        elif ThermostatState.FAN == self.__state:
            if couldHeat and temperature < h1:
                self.__changeState(ThermostatState.HEATING)
            elif couldCool and temperature > c1:
                self.__changeState(ThermostatState.COOLING)
            elif modeOff and not self.__fanRunoutInvoker.isQueued:
                self.__changeState(ThermostatState.OFF)
        else:
            raise RuntimeError(f"Encountered unknown state {self.__state}")

    def __userThermostatInteraction(
            self, event: UserThermostatInteractionEvent):
        if event.interaction == UserThermostatInteractionEvent.MODE_NEXT:
            self._nextMode()
        if event.interaction == UserThermostatInteractionEvent.COMFORT_LOWER:
            self._modifyComfortSettings(-1)
        if event.interaction == UserThermostatInteractionEvent.COMFORT_RAISE:
            self._modifyComfortSettings(1)

    def _modifyComfortSettings(self, increment: int):
        settings = self._getService(Settings)

        self.__backlightReset()
        if Settings.Mode.HEAT == settings.mode:
            settings.comfortMin = settings.comfortMin + increment
        if Settings.Mode.COOL == settings.mode:
            settings.comfortMax = settings.comfortMax + increment
        self.__sampleSensorsInvoker.reset()

    def _nextMode(self):
        settings = self._getService(Settings)

        self.__backlightReset()
        settings.mode = Settings.Mode(
            (int(settings.mode.value)+1) % len(Settings.Mode))
        self.__sampleSensorsInvoker.reset()

    def __changeState(self, newState: ThermostatState):
        if self.__state != newState:
            log.debug(f"Thermostat state {self.__state} -> {newState}")
            self.__relayMap[self.__state].openRelay()
            self.__relayMap[newState].closeRelay()
            if newState.shouldAlsoRunFan:
                self.__relayMap[ThermostatState.FAN].closeRelay()
            self.__state = newState
            self._fireEvent(ThermostatStateChangedEvent(newState))

    def __relayCallback(self, relay: GenericRelay):
        self.__relayToggled = True
        self.__relayToggledTimeoutInvoker.reset()
        log.debug("Driver ENTERING relay toggle timeout")

    def __relayToggledTimeout(self):
        self.__relayToggled = False
        log.debug("Driver COMPLETED relay toggle timeout")

    def __fanRunout(self):
        settings = self._getService(Settings)

        if self.__state == ThermostatState.FAN and \
                settings.mode != Settings.Mode.FAN:
            self.__changeState(ThermostatState.OFF)

    def __backlightReset(self):
        if not self.__backlightTimeoutInvoker.isQueued:
            self.__lcd.setBacklight(True)
            self.__lcd.commit()
        self.__backlightTimeoutInvoker.reset()

    def __backlightTimeout(self):
        self.__lcd.setBacklight(False)

    def __openAllRelays(self):
        for relay in self.__relayMap.values():
            relay.openRelay()

    def _powerPriceChanged(self, event: PowerPriceChangedEvent):
        settings = self._getService(Settings)

        settings.priceChanged(event.price)
        self.__lastPrice = event.price
        self.__drawRowTwoInvoker.reset(2)
        self.__drawRowTwoInvoker.invokeCurrent()

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        settings = self._getService(Settings)
        log.debug(f"New settings: {settings}")
        self.__drawLcdDisplay()
        self.__drawRowTwoInvoker.reset(0)
        self.__drawRowTwoInvoker.invokeCurrent()

    def __processStateChanged(self, event: ThermostatStateChangedEvent):
        self.__lastState = event.state
        self.__drawLcdDisplay()
        self.__drawRowTwoInvoker.reset(1)
        self.__drawRowTwoInvoker.invokeCurrent()

    def __processSensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.__drawLcdDisplay()

    def __drawRowTwoTarget(self):
        settings = self._getService(Settings)

        heat = settings.comfortMin
        cool = settings.comfortMax
        self.__lcd.update(1, 0, f'Target:      {heat:<3.0f}/{cool:>3.0f}')
        self.__lcd.commit()

    def __drawRowTwoState(self):
        state = str(self.__lastState).replace('ThermostatState.', '')
        self.__lcd.update(1, 0, f'State:{state:>14s}')
        self.__lcd.commit()

    def __drawRowTwoPrice(self):
        price = self.__lastPrice
        self.__lcd.update(1, 0, f'Price:  ${price:.4f}/kW*h')
        self.__lcd.commit()

    def __drawRowTwoProgram(self):
        settings = self._getService(Settings)
        name = settings.currentProgram.name
        self.__lcd.update(1, 0, f'Program: {name:>11s}')
        self.__lcd.commit()

    def __drawLcdDisplay(self):
        settings = self._getService(Settings)

        now = self.__lastTemperature
        mode = str(settings.mode).replace('Mode.', '')
        self.__lcd.update(0, 0, f'Now: {now:<5.1f}    {mode:>6s}')
        self.__lcd.update(3, 0, r'UP  DOWN  MODE  NEXT')
        self.__lcd.commit()
