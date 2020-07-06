from enum import Enum


class ThermostatState(Enum):
    """ Represents the state the thermostat is in now.

    This should not be confused with mode, as mode is what the user has
    asked the thermostat to target (e.g. HEAT).  The mode could be HEAT but
    the state could be OFF """
    OFF = 0
    COOLING = 1
    HEATING = 2
    FAN = 3

    def __str__(self):
        return super().__str__().replace('ThermostatState.', '')

    @property
    def shouldAlsoRunFan(self):
        """ Returns true if this state implies the use of the fan """
        return self == ThermostatState.HEATING or \
            self == ThermostatState.COOLING
