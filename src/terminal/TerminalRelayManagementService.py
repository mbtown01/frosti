import curses

from .TerminalRedrawEvent import TerminalRedrawEvent
from src.core import EventBusMember, ThermostatState, ServiceProvider
from src.services import RelayManagementService
from src.core.generics import GenericRelay


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

    def openRelay(self):
        super().openRelay()
        self.redraw()

    def closeRelay(self):
        super().closeRelay()
        self.redraw()


class TerminalRelayManagementService(RelayManagementService):
    """ Service interface for relay management.  Subclassed by code tied into
    whatever actual relay exists """

    def __init__(self):
        self.__relayList = (
            TerminalRelay(ThermostatState.HEATING, 4, 0, 32),
            TerminalRelay(ThermostatState.COOLING, 1, 1, 32),
            TerminalRelay(ThermostatState.FAN, 2, 2, 32),
        )

        super().__init__(relays=self.__relayList)

    def setServiceProvider(self, provider: ServiceProvider):
        super().setServiceProvider(provider)

        super()._installEventHandler(
            TerminalRedrawEvent, self.__terminalRedraw)

    def __terminalRedraw(self, event: TerminalRedrawEvent):
        for relay in self.__relayList:
            if relay.function is not ThermostatState.OFF:
                relay.redraw()
