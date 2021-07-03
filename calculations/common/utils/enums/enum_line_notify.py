from enum import Enum


class NotifyGroup(Enum):
    SELL = ("sell", "趕快賣的股票！")
    NORMAL = ("normal", "徘徊不定的股票0.0")
    BAD = ("bad", "好可憐的股票...")
    POTENTIAL = ("potential", "加速度指標：\n篩選「止跌回升」或「加速往上漲」")
    LONG = ("long", "進場做多：\nRSI >= 50%, MA5 >= MA15")
    SHORT = ("short", "進場做空：\nRSI < 50%, MA5 < MA15")

    # def __init__(self, caption, value):
    #     self.caption = caption
    #     self.value = value

    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        for other_value in values[1:]:
            cls._value2member_map_[other_value] = obj
        obj._all_values = values
        return obj

    def __repr__(self):
        return '<%s.%s: %s>' % (
            self.__class__.__name__,
            self._name_,
            ', '.join([repr(v) for v in self._all_values]),
        )

    # @property
    def getCaption(self) -> str:
        return self._all_values[0]

    # @property
    def getValue(self) -> str:
        return self._all_values[1]
