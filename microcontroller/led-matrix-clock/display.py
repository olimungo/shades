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
    def __init__(self, board, position, buffer):
        self._board = board
        self._position = position
        self._pixels = []
        self._buffer = buffer.copy()

    def setBuffer(self, buffer):
        self._buffer = buffer.copy()

    def _update(self):
        for row, px in enumerate(self._pixels):
            self._board.pixel(self._position, row, px)

    def show(self):
        if len(self._buffer) > 0:
            self._pixels = self._buffer.copy()
            self._buffer = []
            self._update()

    def scroll(self):
        if len(self._buffer) > 0:
            if len(self._pixels) > 7:
                self._pixels.pop()

            self._pixels.insert(0, self._buffer.pop())

            while len(self._pixels) < 8:
                self._pixels.append(0)

            self._update()

    def clean(self):
        self._buffer = []
        self._pixels = []


class Char:
    def __init__(self, board, startCol, buffer):
        self._board = board
        self._startColumn = startCol
        self._columns = []
        self._setColumns(buffer)

    def _setColumns(self, buffer):
        columns = []
        for item in buffer:
            bits = "{0:#b}".format(item)[2:]

            column = []
            for bit in bits:
                column.append(int(bit))

            column.reverse()

            while len(column) < 11:
                column.append(0)

            columns.append(column)

        emptyCols = len(self._columns) == 0

        for indexColumn, column in enumerate(columns):
            if emptyCols:
                self._columns.append(
                    Column(self._board, self._startColumn + indexColumn, column)
                )
            else:
                self._columns[indexColumn].setBuffer(column)

    def setChar(self, buffer):
        self._setColumns(buffer)

    def show(self):
        for column in self._columns:
            column.show()

    def scroll(self):
        for column in self._columns:
            column.scroll()

    def clean(self):
        for column in self._columns:
            column.clean()
