from enum import Enum


class ThermostatMode(Enum):
    """ Represents the mode the thermostat is currently working in.

    The mode of the thermostat is set directly by the user """
    OFF = 0
    AUTO = 1
    COOL = 2
    HEAT = 3
    FAN = 4

    def __str__(self):
        return super().__str__().replace('ThermostatMode.', '')
