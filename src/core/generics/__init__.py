# This file is necessary for the tests written in this folder to
# successfully import logic from src

"""
These classes implement a bone-head simple IOC container pattern, where
there is a set of components that need services (ServiceConsumers) and
somewhere there is a component that provides them (ServiceProvider).
"""

from .GenericEnvironmentsensor import GenericEnvironmentSensor
from .GenericLcdDisplay import GenericLcdDisplay
from .GenericRelay import GenericRelay
