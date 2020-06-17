from enum import Enum

from .ConfigService import ConfigService
from src.core import Event, ServiceConsumer, ServiceProvider, EventBus
from src.core.events import PowerPriceChangedEvent


def checkDict(data: dict, name: str, keys: list):
    for key in keys:
        if key not in data:
            raise RuntimeError(f"'{name}' does not contain '{key}'")


class SettingsChangedEvent(Event):
    """ Fired when any property of SettingsService changes """

    def __init__(self):
        super().__init__('SettingsChangedEvent')


class PriceOverride:
    """ Set of overrides for a given price point """

    def __init__(self, config: dict):
        checkDict(config, 'PriceOverride', ['price'])

        self.price = float(config.get('price'))
        self.comfortMin = config.get('comfortMin')
        self.comfortMax = config.get('comfortMax')


class Program:
    """ Captures all the settings as part of a single program.  Programs
    are used to drive different settings at different times of the day """

    def __init__(self, name: str, config: dict):
        self.name = name
        self.__defaults = config.copy()

        self.__priceOverrides = []
        for override in self.__defaults.get('priceOverrides', []):
            self.__priceOverrides.append(PriceOverride(override))
        self.__priceOverrides = sorted(
            self.__priceOverrides, key=lambda v: v.price, reverse=True)

        self.reset()

    @property
    def priceOverrides(self):
        return self.__priceOverrides.copy()

    def reset(self):
        """ Force any changed values back to their defaults """

        checkDict(self.__defaults, 'program', ['comfortMin', 'comfortMax'])
        self.comfortMin = float(self.__defaults['comfortMin'])
        self.comfortMax = float(self.__defaults['comfortMax'])


class Schedule:
    """ Represents a single schedule instance including the set of days it
    runs on and the various program start times """

    class ScheduleTime:
        def __init__(self, minutes: int, program: str):
            self.minutes = minutes
            self.program = program

    def __init__(self, name: str, config: dict):
        self.name = name

        checkName = f"Schedule '{name}''"
        checkDict(config, checkName, ['days', 'times'])
        if 0 == len(config['days']):
            raise RuntimeError(f"Schedule '{name}' has no day entries")
        if 0 == len(config['times']):
            raise RuntimeError(f"Schedule '{name}' has no time entries")
        self.days = config['days']

        self.__times = []
        for t in config['times']:
            checkDict(t, checkName, ['hour', 'minute', 'program'])
            self.__times.append(Schedule.ScheduleTime(
                minutes=60 * t['hour'] + t['minute'],
                program=t['program']))

        self.__times = sorted(
            self.__times, key=lambda t: t.minutes, reverse=True)

    @property
    def scheduleTimes(self):
        """ Get the list of ScheduleTime entries for this schedule """
        return self.__times

    def getProgram(self, hour: int, minute: int):
        """ Returns the name of the program associated with this time """
        for t in self.__times:
            if hour * 60 + minute >= t.minutes:
                return t.program
        return self.__times[0].program


class SettingsService(ServiceConsumer):
    """ Captures the settings for the thermostat.  SettingsService are changed
    by the user during normal thermostat operation, and an event is
    fired when they are changed.
    """

    class Mode(Enum):
        OFF = 0
        AUTO = 1
        COOL = 2
        HEAT = 3
        FAN = 4

    def __init__(self, data: dict = None):
        self.__data = data

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)
        config = self._getService(ConfigService)
        data = self.__data or config.getData()

        eventBus = self._getService(EventBus)
        eventBus.installEventHandler(
            PowerPriceChangedEvent, self.__powerPriceChanged)

        if 'thermostat' not in data:
            raise RuntimeError("No thermostat configuration found")
        if 'programs' not in data['thermostat']:
            raise RuntimeError("No program configuration found in thermostat")
        programs = data['thermostat']['programs']

        self.__delta = config.resolve('thermostat', 'delta', 1.0)
        self.__mode = SettingsService.Mode.AUTO
        self.__lastOverridePrice = None
        self.__isInPriceOverride = False
        self.__priceWindowHistory = []
        self.__priceWindow = None

        self.__programs = {}
        for name in programs:
            self.__programs[name] = Program(name, programs[name])

        defaults = data['thermostat'].get(
            'defaults', {'comfortMin': 70, 'comfortMax': 78})
        comfortMin = defaults.get('comfortMin', 70)
        comfortMax = defaults.get('comfortMax', 78)
        self.__programs['_default'] = Program(
            'default', {'comfortMin': comfortMin, 'comfortMax': comfortMax})
        self.__currentProgram = self.__programs['_default']

        self.__schedules = {}
        if 'schedule' in data['thermostat']:
            schedule = data['thermostat']['schedule']
            for name in schedule:
                self.__schedules[name] = Schedule(name, schedule[name])
                for t in self.__schedules[name].scheduleTimes:
                    if t.program not in self.__programs:
                        raise RuntimeError(
                            f"Schedule '{name}' refers to " +
                            f"program '{t.program}' that is not defined")

    def __repr__(self):
        return f"[{self.__mode}] heatAt: {self.comfortMin} " + \
               f"coolAt: {self.comfortMax}"

    @property
    def currentProgram(self):
        return self.__currentProgram

    @property
    def isInPriceOverride(self):
        return self.__isInPriceOverride

    @property
    def comfortMin(self):
        """ Minimum temperature that is comfortable, anything lower
        and outside the delta needs the thermostat to heat
        """
        return self.__currentProgram.comfortMin

    @comfortMin.setter
    def comfortMin(self, value):
        eventBus = self._getService(EventBus)
        self.__currentProgram.comfortMin = value
        self.__currentProgram.comfortMax = max(
            self.__currentProgram.comfortMax,
            self.__currentProgram.comfortMin + 2 * self.__delta)
        eventBus.fireEvent(SettingsChangedEvent())

    @property
    def comfortMax(self):
        """ Maximum temperature that is comfortable, anything higher
        and outside the delta needs the thermostat to cool
        """
        return self.__currentProgram.comfortMax

    @comfortMax.setter
    def comfortMax(self, value):
        eventBus = self._getService(EventBus)
        self.__currentProgram.comfortMax = value
        self.__currentProgram.comfortMin = min(
            self.__currentProgram.comfortMin,
            self.__currentProgram.comfortMax - 2 * self.__delta)
        eventBus.fireEvent(SettingsChangedEvent())

    def timeChanged(self, day: int, hour: int, minute: int):
        """ Called when a relevent amount of time has passed so any new
        settings can potentially be applied."""
        eventBus = self._getService(EventBus)
        for name in self.__schedules:
            schedule = self.__schedules[name]
            if day in schedule.days:
                pName = schedule.getProgram(hour, minute)
                if pName not in self.__programs:
                    raise RuntimeError(
                        f"Schedule refers to non-existant program '{pName}")
                newProgram = self.__programs[pName]
                if self.__currentProgram.name != newProgram.name:
                    newProgram.reset()
                    self.__currentProgram = newProgram
                    eventBus.fireEvent(SettingsChangedEvent())

    def __powerPriceChanged(self, event: PowerPriceChangedEvent):
        """ Based on a new power price searches the price overrides to
        determine whether the min/max values need updating and if so,
        applies the new settings.  Returs True if new settings were applied,
        False otherwise """
        eventBus = self._getService(EventBus)

        # Here we're simply assuming that price average resets every 15
        # minutes.  In production we'll get an update roughly every 5
        # minutes and the average of the three is the correct price to
        # use when looking up an override value
        priceWindow = int(eventBus.now/900)
        if self.__priceWindow != priceWindow:
            self.__priceWindow = priceWindow
            self.__priceWindowHistory = []

        self.__priceWindowHistory.append(event.price)
        priceAverage = \
            sum(self.__priceWindowHistory)/len(self.__priceWindowHistory)

        eventBus = self._getService(EventBus)
        for override in self.__currentProgram.priceOverrides:
            if priceAverage >= override.price:
                if self.__lastOverridePrice == override.price:
                    return

                self.__lastOverridePrice = override.price
                self.__isInPriceOverride = True
                if override.comfortMin is not None:
                    self.__currentProgram.comfortMin = override.comfortMin
                    eventBus.fireEvent(SettingsChangedEvent())
                if override.comfortMax is not None:
                    self.__currentProgram.comfortMax = override.comfortMax
                    eventBus.fireEvent(SettingsChangedEvent())
                return

        if self.__lastOverridePrice is not None:
            self.__currentProgram.reset()
            self.__lastOverridePrice = None
            self.__isInPriceOverride = False
            eventBus.fireEvent(SettingsChangedEvent())

    @property
    def mode(self):
        """ The current mode the thermostat is in """
        return self.__mode

    @mode.setter
    def mode(self, value):
        eventBus = self._getService(EventBus)
        self.__mode = value
        eventBus.fireEvent(SettingsChangedEvent())
