import curses

from src.core.generics import GenericLcdDisplay


class TerminalDisplay(GenericLcdDisplay):

    # Modified version of the driver from
    # https://github.com/sunfounder/SunFounder_SensorKit_for_RPi2.git
    def __init__(self, window, colorPair, width, height):
        super().__init__(width, height)
        self.__window = window
        self.__colorPair = colorPair
        self.__backlightEnabled = False

    def setBacklight(self, enabled: bool):
        self.__backlightEnabled = enabled
        self.refresh()

    def refresh(self):
        self.__window.clear()
        for row in range(super().height):
            color = self.__colorPair
            if self.__backlightEnabled:
                color = color | curses.A_REVERSE
            self.__window.addstr(row, 0, super().rowText(row), color)
        self.__window.refresh()

    def commit(self):
        """ Commits all pending changes to the display """
        changed = False
        results = super().commit()
        for i in range(len(results)):
            for change in results[i]:
                color = self.__colorPair
                if self.__backlightEnabled:
                    color = color | curses.A_REVERSE
                self.__window.addstr(i, change[0], change[1], color)
                changed = True
        if changed:
            self.__window.refresh()
