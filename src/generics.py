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
        """ A row of text on a generic cursor-based LCD display """

        def __init__(self, width: int):
            self.__buffer = list()
            self.__updates = list()
            self.__width = width
            self.__isInvalid = False
            for _ in range(self.__width):
                self.__buffer.append(' ')
                self.__updates.append(' ')

        @property
        def text(self):
            return ''.join(self.__buffer)

        def update(self, offset: int, text: str):
            """ Write 'text' at the specified offset on the row """
            if offset < 0:
                text = text[abs(offset):]
                offset = 0
            for i in range(min(self.__width-offset, len(text))):
                self.__updates[i+offset] = text[i]

        def commit(self):
            """ Commit all pending updates and build a list of changes """
            results = list()
            offset = 0
            while offset < self.__width:
                change = list()
                while offset+len(change) < self.__width and \
                        self.__updates[offset+len(change)] != \
                        self.__buffer[offset+len(change)]:
                    self.__buffer[offset+len(change)] = \
                        self.__updates[offset+len(change)]
                    change.append(self.__updates[offset+len(change)])
                if len(change):
                    results.append([offset, ''.join(change)])
                offset += len(change) + 1

            return results

    def __init__(self, width: int, height: int):
        self.__rows = list()
        for _ in range(height):
            self.__rows.append(GenericScreen.Row(width))

    @property
    def text(self):
        rowText = list()
        for row in self.__rows:
            rowText.append(row.text)
        return '\n'.join(rowText)

    def update(self, row: int, col: int, text: str):
        if row >= len(self.__rows):
            raise RuntimeError(
                f"Row {row} is out of range, max={len(self.__rows)-1}")
        self.__rows[row].update(col, text)

    def commit(self):
        results = list()
        for row in self.__rows:
            results.append(row.commit())

        return results
