fonts = [
    [0xFF, 0x81, 0xFF, 0xFF],  # 0
    [0x04, 0x02, 0xFF, 0xFF],  # 1
    [0xF1, 0xF9, 0x8F, 0x86],  # 2
    [0x89, 0x89, 0xFF, 0xFF],  # 3
    [0x0F, 0x08, 0xF8, 0xFC],  # 4
    [0x8F, 0x8F, 0xF9, 0xF9],  # 5
    [0xFF, 0x88, 0xF8, 0xF8],  # 6
    [0x01, 0x01, 0xFF, 0xFF],  # 7
    [0xFF, 0x89, 0xFF, 0xFF],  # 8
    [0x0F, 0x09, 0xFF, 0xFF],  # 9
    [0x24],  # colon :
    [0x00],  # blank
]


class Column:
    def __init__(self, board, position, column):
        self._board = board
        self._position = position
        self._columnToDisplay = 0
        self._columnBuffer = column
        self._scrollCount = 0

    def setBuffer(self, column):
        self._columnBuffer = column
        self._scrollCount = 8

    def _update(self):
        columnToDisplay = self._columnToDisplay

        for row in range(8):
            # Get the lowest bit (the one on the right)
            pixel = columnToDisplay & 1
            self._board.pixel(self._position, row, pixel)
            
            # Move the bits to the right (divide by 2)
            columnToDisplay = columnToDisplay >> 1

    def show(self):
        self._columnToDisplay = self._columnBuffer
        self._update()

    def scroll(self):
        if self._scrollCount > 0:
            self._scrollCount -= 1

            # Check if the highest bit (the one on the left) is set
            pixel = 0
            if self._columnBuffer & 128 > 0:
                pixel = 1

            # Move the bits to the left (multiply by 2) and keep only the 8th first bits
            self._columnBuffer = (self._columnBuffer << 1) & 255

            # Move the bits to the left (multiply by 2), keep only the 8th first bits and set
            # the lowest bit
            self._columnToDisplay = ((self._columnToDisplay << 1) & 255) + pixel

            self._update()

    def clean(self):
        self._columnBuffer = 0
        self._columnToDisplay = 0


class Char:
    def __init__(self, board, startColumn, columns):
        self._board = board
        self._startColumn = startColumn
        self._columns = []

        for indexColumn in range(len(columns)):
            self._columns.append(Column(self._board, self._startColumn + indexColumn, []))

        self.setBuffer(columns)

    def setBuffer(self, columns):
        for indexColumn, column in enumerate(columns):
            self._columns[indexColumn].setBuffer(column)

    def show(self):
        for column in self._columns:
            column.show()

    def scroll(self):
        for column in self._columns:
            column.scroll()

    def clean(self):
        for column in self._columns:
            column.clean()
