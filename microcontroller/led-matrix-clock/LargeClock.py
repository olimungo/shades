from display import fonts, Char
from machine import Timer


class LargeClock:
    _hour1 = _hour2 = _minute1 = _minute2 = _second1 = _second2 = -1
    _tickTimer = Timer(-1)
    _refreshTimer = Timer(-1)
    _cleanTimer = Timer(-1)

    def __init__(self, board, time):
        self._time = time
        self._board = board

        self._digit1 = Char(board, 0, fonts[0])
        self._digit2 = Char(board, 5, fonts[0])
        self._digit3 = Char(board, 12, fonts[0])
        self._digit4 = Char(board, 17, fonts[0])
        self._digit5 = Char(board, 23, fonts[0])
        self._digit6 = Char(board, 28, fonts[0])
        self._colon = Char(board, 10, fonts[10])

    def _tick(self, timer=None):
        hour1, hour2, minute1, minute2, second1, second2 = self._time.getTime()

        if second2 % 2:
            colon = fonts[10]
        else:
            colon = fonts[11]

        self._checkUpdate(self._digit1, self._hour1, hour1, fonts[hour1])
        self._checkUpdate(self._digit2, self._hour2, hour2, fonts[hour2])
        self._checkUpdate(self._digit3, self._minute1, minute1, fonts[minute1])
        self._checkUpdate(self._digit4, self._minute2, minute2, fonts[minute2])
        self._checkUpdate(self._digit5, self._second1, second1, fonts[second1])
        self._checkUpdate(self._digit6, self._second2, second2, fonts[second2])
        self._checkUpdate(self._colon, self._second2, second2, colon)

        self._hour1 = hour1
        self._hour2 = hour2
        self._minute1 = minute1
        self._minute2 = minute2
        self._second1 = second1
        self._second2 = second2

    def _refresh(self, timer=None):
        self._digit1.scroll()
        self._digit2.scroll()
        self._colon.show()
        self._digit3.scroll()
        self._digit4.scroll()
        self._digit5.scroll()
        self._digit6.scroll()

        self._board.show()

    def _checkUpdate(self, elem, prevVal, newVal, value):
        if prevVal != newVal:
            elem.setBuffer(value)

    def _clean(self, timer=None):
        self._board.fill(0)
        self._board.show()

        self._hour1 = self._hour2 = -1
        self._minute1 = self._minute2 = -1
        self._second1 = self._second2 = -1

        self._digit1.clean()
        self._digit2.clean()
        self._colon.clean()
        self._digit3.clean()
        self._digit4.clean()
        self._digit5.clean()
        self._digit6.clean()

    def start(self):
        self._tick()
        self._refresh()
        self._tickTimer.init(period=250, mode=Timer.PERIODIC, callback=self._tick)
        self._refreshTimer.init(period=35, mode=Timer.PERIODIC, callback=self._refresh)

    def stop(self):
        self._refreshTimer.deinit()
        self._tickTimer.deinit()

        self._cleanTimer.init(period=50, mode=Timer.ONE_SHOT, callback=self._clean)

