import curses

from src.core.generics import GenericRgbLed


class TerminalRgbLed(GenericRgbLed):
    """ Simple three-color RGB LED that can only be in 8 states """

    def __init__(self, window):
        self.__displayWin = window
        self.__color = GenericRgbLed.Color.WHITE

    def setColor(self, color: GenericRgbLed.Color):
        self.__color = color
        self.redraw()

    def redraw(self):
        colorPair = curses.color_pair(self.__color.value)
        y, _ = self.__displayWin.getmaxyx()
        self.__displayWin.clear()
        for y in range(y):
            self.__displayWin.addstr(y, 0, '**', curses.A_REVERSE | colorPair)
        self.__displayWin.refresh()
