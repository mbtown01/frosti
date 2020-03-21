import curses

from src.core.generics import GenericRgbLed


class TerminalRgbLed(GenericRgbLed):
    """ Simple three-color RGB LED that can only be in 8 states """

    def __init__(self):
        pass

    def setColor(self, color: GenericRgbLed.Color):
        pass
