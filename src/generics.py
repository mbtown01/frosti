from enum import Enum
from time import time, localtime
import atexit

from src.logging import log
from src.settings import settings, Settings, SettingsChangedEvent
from src.events import EventBus, EventHandler, Event, TimerBasedHandler
from src.config import config


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


class ThermostatState(Enum):
    OFF = 0
    COOLING = 1
    HEATING = 2
    FAN = 3


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

    @property
    def isOpen(self):
        """  True if open, False if closed, None if indeterminite """
        return self.__isOpen

    @property
    def function(self):
        """ Gets the ThermostatState function this relay handles """
        return self.__function

    def openRelay(self):
        """ Open the relay, break circuit, disabling the function """
        self.__isOpen = True

    def closeRelay(self):
        """ Close the relay, connect circuit, enabling the function """
        self.__isOpen = False


class GenericThermostatDriver(EventHandler):

    def __init__(self,
                 lcd: GenericLcdDisplay,
                 sensor: GenericEnvironmentSensor,
                 relays: list,
                 eventBus: EventBus):
        super().__init__(eventBus)

        self.__delta = \
            config.value('thermostat').value('delta', 1.0)
        self.__fanRunoutDuration = \
            config.value('thermostat').value('fanRunout', 30)
        self.__backlightTimeoutDuration = \
            config.value('thermostat').value('backlightTimeout', 10)

        self.__lcd = lcd
        self.__sensor = sensor
        self.__relayMap = {r.function: r for r in relays}
        self.__state = ThermostatState.OFF
        self.__lcd.setBacklight(True)
        self.__inBacklightTimeout = True
        self.__inFanRunout = False
        self.__lastTemperature = 0.0
        self.__lastState = ThermostatState.OFF
        self.__lastPrice = 0.0

        self._sampleSensorsInvoker = self._installTimerHandler(
            frequency=5.0, handlers=[self.sampleSensors])
        self.__checkScheduleInvoker = self._installTimerHandler(
            frequency=5.0, handlers=[self.checkSchedule])
        self.__backlightTimeoutInvoker = self._installTimerHandler(
            frequency=self.__backlightTimeoutDuration,
            handlers=[self.__backlightTimeout])
        self.__fanRunoutInvoker = self._installTimerHandler(
            frequency=self.__fanRunoutDuration,
            handlers=[self.__fanRunout])
        # self.__drawLcdInvoker = self._installTimerHandler(
        #     frequency=1.0, handlers=[self.__drawLcdDisplay])
        self.__drawRowTwoInvoker = self._installTimerHandler(
            frequency=3.0, handlers=[
                self.__drawRowTwoTarget,
                self.__drawRowTwoState,
                self.__drawRowTwoPrice])

        self._installEventHandler(
            SettingsChangedEvent, self.__processSettingsChanged)
        self._installEventHandler(
            SensorDataChangedEvent, self.__processSensorDataChanged)
        self._installEventHandler(
            ThermostatStateChangedEvent, self.__processStateChanged)
        self._installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)

        self.__openAllRelays()
        self.checkSchedule()
        self.sampleSensors()
        # atexit.register(self.__openAllRelays, self=self)

    @property
    def state(self):
        """ Current state of the thermostat """
        return self.__state

    def checkSchedule(self):
        values = self._getLocalTime()
        settings.timeChanged(
            day=values.tm_wday, hour=values.tm_hour, minute=values.tm_min)

    def sampleSensors(self):
        temperature = self.__sensor.temperature
        super()._fireEvent(SensorDataChangedEvent(
            temperature=temperature,
            pressure=self.__sensor.pressure,
            humidity=self.__sensor.humidity
        ))

        if settings.mode == Settings.Mode.COOL:
            self.__processCooling(temperature)
        elif settings.mode == Settings.Mode.HEAT:
            self.__processHeating(temperature)
        elif settings.mode == Settings.Mode.AUTO:
            self.__processAuto(temperature)
        else:
            self.__changeState(ThermostatState.OFF)

    def _getLocalTime(self):
        return localtime(time())

    def _modifyComfortSettings(self, increment: int):
        if Settings.Mode.HEAT == settings.mode:
            settings.comfortMin = settings.comfortMin + increment
        if Settings.Mode.COOL == settings.mode:
            settings.comfortMax = settings.comfortMax + increment

    def __fanRunout(self):
        self.__relayMap[ThermostatState.FAN].openRelay()
        self.__inFanRunout = False

    def __backlightTimeout(self):
        self.__inBacklightTimeout = False
        self.__lcd.setBacklight(False)

    def _powerPriceChanged(self, event: PowerPriceChangedEvent):
        settings.priceChanged(event.price)

    def __openAllRelays(self):
        for relay in self.__relayMap.values():
            relay.openRelay()

    def __processCooling(self, newTemp: float):
        runAt = settings.comfortMax+self.__delta
        runUntil = settings.comfortMax-self.__delta

        if self.__state != ThermostatState.COOLING and newTemp > runAt:
            self.__changeState(ThermostatState.COOLING)
        elif newTemp <= runUntil:
            self.__changeState(ThermostatState.OFF)

    def __processHeating(self, newTemp: float):
        runAt = settings.comfortMin-self.__delta
        runUntil = settings.comfortMin+self.__delta

        if self.__state != ThermostatState.HEATING and newTemp < runAt:
            self.__changeState(ThermostatState.HEATING)
        elif newTemp >= runUntil:
            self.__changeState(ThermostatState.OFF)

    def __processAuto(self, newTemp: float):
        runAtHeat = settings.comfortMin-self.__delta
        runUntilHeat = settings.comfortMin+self.__delta
        runAtCool = settings.comfortMax+self.__delta
        runUntilCool = settings.comfortMax-self.__delta

        if self.__state != ThermostatState.COOLING and newTemp > runAtCool:
            self.__changeState(ThermostatState.COOLING)
        elif self.__state != ThermostatState.HEATING and newTemp < runAtHeat:
            self.__changeState(ThermostatState.HEATING)
        elif newTemp >= runUntilHeat and newTemp <= runUntilCool:
            self.__changeState(ThermostatState.OFF)

    def __changeState(self, newState: ThermostatState):
        if self.__state != newState:
            if self.__state in self.__relayMap:
                self.__relayMap[self.__state].openRelay()
            self.__state = newState
            self.__inFanRunout = ThermostatState.OFF == newState
            if ThermostatState.OFF != newState:
                self.__relayMap[newState].closeRelay()
                self.__relayMap[ThermostatState.FAN].closeRelay()
                self.__fanRunoutInvoker.reset()
            self._fireEvent(ThermostatStateChangedEvent(newState))

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        log.info(f"DefaultScreen: Power price is now {event.price:.4f}/kW*h")
        self.__lastPrice = event.price
        self.__drawRowTwoInvoker.reset(2)
        self.__drawRowTwoInvoker.invokeCurrent()

    def __processSettingsChanged(self, event: SettingsChangedEvent):
        log.debug(f"DefaultScreen: new settings: {settings}")
        self.__drawRowTwoInvoker.reset(0)
        self.__drawRowTwoInvoker.invokeCurrent()

    def __processStateChanged(self, event: ThermostatStateChangedEvent):
        log.debug(f"DefaultScreen: new state: {event.state}")
        self.__lastState = event.state
        self.__drawRowTwoInvoker.reset(1)
        self.__drawRowTwoInvoker.invokeCurrent()

    def __drawRowTwoTarget(self):
        heat = settings.comfortMin
        cool = settings.comfortMax
        self.__lcd.update(1, 0, f'Target:      {heat:<3.0f}/{cool:>3.0f}')
        self.__lcd.commit()

    def __processSensorDataChanged(self, event: SensorDataChangedEvent):
        self.__lastTemperature = event.temperature
        self.__drawLcdDisplay()

    def __drawRowTwoState(self):
        state = str(self.__lastState).replace('ThermostatState.', '')
        self.__lcd.update(1, 0, f'State:     {state:>9s}')
        self.__lcd.commit()

    def __drawRowTwoPrice(self):
        price = self.__lastPrice
        self.__lcd.update(1, 0, f'Price:  ${price:.4f}/kW*h')
        self.__lcd.commit()

    def __drawLcdDisplay(self):
        now = self.__lastTemperature
        mode = str(settings.mode).replace('Mode.', '')
        self.__lcd.update(0, 0, f'Now: {now:<5.1f}    {mode:>6s}')
        self.__lcd.update(3, 0, r'UP  DOWN  MODE  NEXT')
        self.__lcd.commit()
