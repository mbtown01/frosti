# This file is necessary for the tests written in this folder to
# successfully import logic from frosti

"""
These classes implement a bone-head simple IOC container pattern, where
there is a set of components that need services (ServiceConsumers) and
somewhere there is a component that provides them (ServiceProvider).
"""

from .ThermostatStateChangingEvent import ThermostatStateChangingEvent
from .ThermostatStateChangedEvent import ThermostatStateChangedEvent
from .PowerPriceChangedEvent import PowerPriceChangedEvent
from .SensorDataChangedEvent import SensorDataChangedEvent
from .SettingsChangedEvent import SettingsChangedEvent
