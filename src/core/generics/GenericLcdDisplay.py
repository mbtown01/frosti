class GenericLcdDisplay:
    """ Generic implementation of a multi-line LCD with a cursor-based
    interface """

    class Row:
        """ A row of text on a generic cursor-based LCD display """

        def __init__(self, width: int):
            self.__width = width
            self.clear()

        @property
        def text(self):
            return ''.join(self.__buffer)

        def clear(self):
            self.__buffer = list()
            self.__updates = list()
            for _ in range(self.__width):
                self.__buffer.append(' ')
                self.__updates.append(' ')

        def update(self, offset: int, text: str):
            """ Write 'text' at the specified offset on the row """
            if offset < 0:
                text = text[abs(offset):]
                offset = 0
            for i in range(min(self.__width - offset, len(text))):
                self.__updates[i + offset] = text[i]

        def commit(self):
            """ Commit all pending updates and build a list of changes """
            results = list()
            offset = 0
            while offset < self.__width:
                change = list()
                while offset + len(change) < self.__width and \
                        self.__updates[offset + len(change)] != \
                        self.__buffer[offset + len(change)]:
                    self.__buffer[offset + len(change)] = \
                        self.__updates[offset + len(change)]
                    change.append(self.__updates[offset + len(change)])
                if len(change):
                    results.append([offset, ''.join(change)])
                offset += len(change) + 1

            return results

    def __init__(self, width: int, height: int):
        self.__rows = list()
        self.__width = width
        self.__height = height

        for _ in range(height):
            self.__rows.append(GenericLcdDisplay.Row(width))

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    @property
    def text(self):
        rowText = list()
        for row in self.__rows:
            rowText.append(row.text)
        return '\n'.join(rowText)

    def rowText(self, row: int):
        return self.__rows[row].text

    def clear(self):
        """ Clear all rows and pending updates """
        for row in self.__rows:
            row.clear()

    def setBacklight(self, enabled: bool):
        pass

    def update(self, row: int, col: int, text: str):
        """ Add a pending change to the display """
        if row >= len(self.__rows):
            raise RuntimeError(
                f"Row {row} is out of range, max={len(self.__rows)-1}")
        self.__rows[row].update(col, text)

    def commit(self):
        """ Commit the set of pending changes and return the changes from
        the previous commit """
        results = list()
        for row in self.__rows:
            results.append(row.commit())

        return results
