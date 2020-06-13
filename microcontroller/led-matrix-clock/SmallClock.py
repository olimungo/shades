from display import fonts, Char, Column
from machine import Timer


class SmallClock:
    _hour1 = _hour2 = _minute1 = _minute2 = _second = _numBars = -1
    _showColon = False
    _tickTimer = Timer(-1)
    _refreshTimer = Timer(-1)
    _cleanTimer = Timer(-1)

    def __init__(self, board, time):
        self._time = time
        self._board = board

        self._digit1 = Char(board, 3, fonts[0])
        self._digit2 = Char(board, 8, fonts[0])
        self._digit3 = Char(board, 15, fonts[0])
        self._digit4 = Char(board, 20, fonts[0])
        self._colon = Char(board, 13, fonts[10])
        self._bar1 = Column(board, 27, fonts[11])
        self._bar2 = Column(board, 28, fonts[11])

    def _tick(self, timer=None):
        hour1, hour2, minute1, minute2, second1, second2 = self._time.getTime()

        second = second1 * 10 + second2
        numBars = int(second / (60 / 9))  # 9 states = 8 lights + no light
        column = self._createBar(numBars)

        if second2 % 2:
            colon = fonts[10]
        else:
            colon = fonts[11]

        self._checkUpdate(self._digit1, self._hour1, hour1, fonts[hour1])
        self._checkUpdate(self._digit2, self._hour2, hour2, fonts[hour2])
        self._checkUpdate(self._digit3, self._minute1, minute1, fonts[minute1])
        self._checkUpdate(self._digit4, self._minute2, minute2, fonts[minute2])
        self._checkUpdate(self._bar1, self._numBars, numBars, column)
        self._checkUpdate(self._bar2, self._numBars, numBars, column)
        self._checkUpdate(self._colon, self._second, second, colon)

        self._hour1 = hour1
        self._hour2 = hour2
        self._minute1 = minute1
        self._minute2 = minute2
        self._second = second
        self._numBars = numBars

    def _refresh(self, timer=None):
        self._digit1.scroll()
        self._digit2.scroll()
        self._colon.show()
        self._digit3.scroll()
        self._digit4.scroll()

        if self._second == 0:
            self._bar1.scroll()
            self._bar2.scroll()
        else:
            self._bar1.show()
            self._bar2.show()

        self._board.show()

    def _checkUpdate(self, elem, prevVal, newVal, value):
        if prevVal != newVal:
            elem.setBuffer(value)

    def _clean(self, timer=None):
        self._board.fill(0)
        self._board.show()

        self._hour1 = self._hour2 = -1
        self._minute1 = self._minute2 = -1
        self._second = -1

        self._digit1.clean()
        self._digit2.clean()
        self._colon.clean()
        self._digit3.clean()
        self._digit4.clean()
        self._bar1.clean()
        self._bar2.clean()

    def _createBar(self, numBars):
        column = 0

        for i in range(numBars):
            column = (column << 1) + 1

        for i in range(0, 8 - numBars):
            column <<= 1

        return column

    def start(self):
        self._tick()
        self._refresh()
        self._tickTimer.init(period=250, mode=Timer.PERIODIC, callback=self._tick)
        self._refreshTimer.init(period=35, mode=Timer.PERIODIC, callback=self._refresh)

    def stop(self):
        self._refreshTimer.deinit()
        self._tickTimer.deinit()

        self._cleanTimer.init(period=50, mode=Timer.ONE_SHOT, callback=self._clean)

