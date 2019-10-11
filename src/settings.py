from enum import Enum

from src.events import Event, EventBus, EventHandler
from src.logging import log
from src.config import Config
from src.services import ServiceProvider


class SettingsChangedEvent(Event):
    def __init__(self):
        super().__init__('SettingsChangedEvent')


class PriceOverride:
    """ Set of overrides for a given price point """
    def __init__(self, config: dict):
        if 'price' not in config:
            raise RuntimeError("Override does not contain 'price'")

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

        if 'comfortMin' not in self.__defaults:
            raise RuntimeError(
                f"Parameter 'comfortMin' not in program '{self.name}'")
        if 'comfortMax' not in self.__defaults:
            raise RuntimeError(
                f"Parameter 'comfortMax' not in program '{self.name}'")
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

        if 'days' not in config:
            raise RuntimeError(f"Schedule '{name}' does not contain 'days'")
        if 0 == len(config['days']):
            raise RuntimeError(f"Schedule '{name}' has no day entries")
        self.days = config['days']

        if 'times' not in config:
            raise RuntimeError(f"Schedule '{name}' does not contain 'times'")
        if 0 == len(config['times']):
            raise RuntimeError(f"Schedule '{name}' has no time entries")

        self.__times = []
        for t in config['times']:
            if 'hour' not in t:
                raise RuntimeError(
                    f"Schedule '{name}' 'times' entry missing 'hour'")
            if 'minute' not in t:
                raise RuntimeError(
                    f"Schedule '{name}' 'times' entry missing 'minute'")
            if 'program' not in t:
                raise RuntimeError(
                    f"Schedule '{name}' 'times' entry missing 'program'")
            self.__times.append(Schedule.ScheduleTime(
                minutes=60*t['hour']+t['minute'],
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
            if hour*60+minute >= t.minutes:
                return t.program
        return self.__times[0].program


class Settings(EventHandler):
    """ Captures the settings for the thermostat.  Settings are changed
    by the user during normal thermostat operation, and an event is
    fired when they are changed.
    """

    class Mode(Enum):
        OFF = 0
        AUTO = 1
        COOL = 2
        HEAT = 3
        FAN = 4

    def __init__(self, json: dict=None):
        self.__data = json

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)
        config = self._getService(Config)
        json = self.__data or config.getJson()

        if 'thermostat' not in json:
            raise RuntimeError("No thermostat configuration found")
        if 'programs' not in json['thermostat']:
            raise RuntimeError("No program configuration found in thermostat")
        programs = json['thermostat']['programs']
        if '_default' not in programs:
            raise RuntimeError(f"No default program configured")

        self.__delta = config.resolve('thermostat', 'delta', 1.0)
        self.__mode = Settings.Mode.AUTO
        self.__lastOverridePrice = None
        self.__programs = {}
        for name in programs:
            self.__programs[name] = Program(name, programs[name])
        self.__currentProgram = self.__programs['_default']

        self.__schedules = {}
        if 'schedule' in json['thermostat']:
            schedule = json['thermostat']['schedule']
            for name in schedule:
                self.__schedules[name] = Schedule(name, schedule[name])
                for t in self.__schedules[name].scheduleTimes:
                    if t.program not in self.__programs:
                        raise RuntimeError(
                            f"Schedule '{name}' refers to " +
                            f"bad program '{t.program}'")

    def __repr__(self):
        return f"[{self.__mode}] heatAt: {self.comfortMin} " + \
               f"coolAt: {self.comfortMax}"

    @property
    def comfortMin(self):
        """ Minimum temperature that is comfortable, anything lower
        and outside the delta needs the thermostat to heat
        """
        return self.__currentProgram.comfortMin

    @comfortMin.setter
    def comfortMin(self, value):
        self.__currentProgram.comfortMin = value
        self.__currentProgram.comfortMax = max(
            self.__currentProgram.comfortMax,
            self.__currentProgram.comfortMin+2*self.__delta)
        self._fireEvent(SettingsChangedEvent())

    @property
    def comfortMax(self):
        """ Maximum temperature that is comfortable, anything higher
        and outside the delta needs the thermostat to cool
        """
        return self.__currentProgram.comfortMax

    @comfortMax.setter
    def comfortMax(self, value):
        self.__currentProgram.comfortMax = value
        self.__currentProgram.comfortMin = min(
            self.__currentProgram.comfortMin,
            self.__currentProgram.comfortMax-2*self.__delta)
        self._fireEvent(SettingsChangedEvent())

    def timeChanged(self, day: int, hour: int, minute: int):
        for name in self.__schedules:
            schedule = self.__schedules[name]
            if day in schedule.days:
                pName = schedule.getProgram(hour, minute)
                if pName not in self.__programs:
                    raise RuntimeError(
                        f"Schedule refers to non-existant program 'program'")
                newProgram = self.__programs[pName]
                if self.__currentProgram.name != newProgram.name:
                    self.__currentProgram = self.__programs[pName]
                    self._fireEvent(SettingsChangedEvent())

    def priceChanged(self, price: float):
        """ Based on a new power price searches the price overrides to
        determine whether the min/max values need updating and if so,
        applies the new settings.  Returs True if new settings were applied,
        False otherwise """
        for override in self.__currentProgram.priceOverrides:
            if price >= override.price:
                if self.__lastOverridePrice == override.price:
                    return False

                self.__lastOverridePrice = override.price
                if override.comfortMin is not None:
                    self.__currentProgram.comfortMin = override.comfortMin
                if override.comfortMax is not None:
                    self.__currentProgram.comfortMax = override.comfortMax
                    self._fireEvent(SettingsChangedEvent())
                return True

        if self.__lastOverridePrice is not None:
            self.__currentProgram.reset()
            self.__lastOverridePrice = None
            self._fireEvent(SettingsChangedEvent())
            return True

        return False

    @property
    def mode(self):
        """ The current mode the thermostat is in """
        return self.__mode

    @mode.setter
    def mode(self, value):
        self.__mode = value
        self._fireEvent(SettingsChangedEvent())
