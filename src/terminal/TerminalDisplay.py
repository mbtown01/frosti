import curses

from src.core.generics import GenericLcdDisplay


class TerminalDisplay(GenericLcdDisplay):

    # Modified version of the driver from
    # https://github.com/sunfounder/SunFounder_SensorKit_for_RPi2.git
    def __init__(self, window, width, height):
        super().__init__(width, height)
        self.__window = window
        self.__backlightEnabled = False

    def setBacklight(self, enabled: bool):
        self.__backlightEnabled = enabled
        self.commit()

    def refresh(self):
        self.__window.refresh()

    def commit(self):
        """ Commits all pending changes to the display """
        changed = False
        results = super().commit()
        for i in range(len(results)):
            for change in results[i]:
                self.__window.addstr(i, change[0], change[1])
                changed = True
        if changed:
            self.__window.refresh()
