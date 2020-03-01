import curses

from src.generics import GenericRelay, ThermostatState


class TerminalRelay(GenericRelay):

    def __init__(self, function: ThermostatState,
                 colorPair: int, row: int, col: int):
        super().__init__(function)

        self.__displayWin = curses.newwin(1, 16, row, col)
        self.__colorPair = curses.color_pair(colorPair)

    def redraw(self):
        self.__displayWin.clear()
        if self.isOpen is None:
            self.__displayWin.addstr(
                0, 0, self.function.name + ' UNKNOWN')
        elif self.isOpen:
            self.__displayWin.addstr(
                0, 0, self.function.name + ' OPEN')
        else:
            self.__displayWin.addstr(
                0, 0, self.function.name + ' CLOSED',
                curses.A_REVERSE | self.__colorPair)

        self.__displayWin.refresh()

    def _openRelay(self):
        self.redraw()

    def _closeRelay(self):
        self.redraw()
