from abc import ABC, abstractmethod

from enum import Enum


class GenericRgbLed(ABC):
    """ Simple three-color RGB LED that can only be in 8 states """

    class Color(Enum):
        BLACK = 0
        BLUE = 1
        GREEN = 2
        CYAN = 3
        RED = 4
        MAGENTA = 5
        YELLOW = 6
        WHITE = 7

    @abstractmethod
    def setColor(self, color: Color):
        pass
