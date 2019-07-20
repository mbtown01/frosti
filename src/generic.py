from src.logging import log
from src.settings import Settings, SettingsChangedEvent
from src.events import EventBus, EventHandler, Event


class GenericButton:
    """ A physical button provided to the user """

    def __init__(self, name: str):
        self.__name = name

    @property
    def name(self):
        return self.__name

    def query(self):
        return False


class GenericScreen:
    """ A specific screen on the LCD with draw and button logic """

    class Row:
        def __init__(self, width: int):
            self.__buffer = list()
            self.__updates = list()
            self.__width = width
            self.__isInvalid = False
            for _ in range(self.__width):
                self.__buffer.append(' ')
                self.__updates.append(' ')

        def update(self, offset: int, update: str):
            for i in range(min(self.__width-offset, len(update))):
                self.__updates[i+offset] = update[offset]

        def finalizeUpdates(self):
            results = {}
            offset = 0
            while offset < self.__width:
                change = list()
                while offset+len(change) < self.__width and \
                        self.__updates[offset+len(change)] != \
                        self.__buffer[offset+len(change)]:
                    change.append(self.__updates[offset+len(change)])
                    self.__buffer[offset+len(change)] = \
                        self.__updates[offset+len(change)]
                if len(change):
                    results[offset] = ''.join(change)
                offset += len(change) + 1

            return results

    def __init__(self, width: int, name: str):
        self.__name = name
        self.__isInvalid = False
        self.__rowOne = GenericScreen.Row(width)
        self.__rowTwo = GenericScreen.Row(width)

    @property
    def name(self):
        return self.__name

    def settingsChanged(self, settings: Settings):
        pass

    def buttonPressed(self, button: GenericButton):
        pass

    def _updateDisplay(self, rowOne: str=None, rowTwo: str=None):
        if rowOne is not None:
            self.__rowOneUpdate = rowOne
        if rowTwo is not None:
            self.__rowTwoUpdate = rowOne
