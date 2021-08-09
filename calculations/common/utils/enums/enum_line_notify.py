from enum import Enum


class NotifyGroup(Enum):
    SELL = ("sell", "😍 趕快賣：")
    NORMAL = ("normal", "😳 徘徊中：")
    BAD = ("bad", "😭 好可憐：")
    POTENTIAL = ("potential", "⛅ 加速度指標：\n篩選「止跌回升」或「加速上漲」")

    """ MA cross rate """
    # LONG = ("long", "📈 進場做多：\nRSI >= 50%, MA5 >= MA15")
    # SHORT = ("short", "📉 進場做空：\nRSI < 50%, MA5 < MA15")

    """ Bolling band """
    SHORT = ("short", "📉 進場做空：\n昨日收盤價在布林通道上緣，今日收盤價低於布林通道上緣")
    LONG = ("long", "📈 進場做多：\nKD黃金交叉，收盤價低於布林通道中線")

    INDEX = ("index", "💘 產業數量(加速度指標)：")

    def __new__(cls, *values):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = values[0]
        for other_value in values[1:]:
            cls._value2member_map_[other_value] = obj

        # 所有value的集合
        obj.all_values = values
        return obj

    def __repr__(self):
        return '<%s.%s: %s>' % (
            self.__class__.__name__,
            self._name_,
            ', '.join([repr(v) for v in self.all_values]),
        )

    # @property
    def getCaption(self) -> str:
        return self.all_values[0]

    # @property
    def getValue(self) -> str:
        return self.all_values[1]

    @classmethod
    def getLineGroup(cls) -> dict:
        return {cls.SELL: [], cls.SHORT: [], cls.LONG: [], cls.NORMAL: [], cls.BAD: []}

    @classmethod
    def getPotentialGroup(cls) -> dict:
        return {cls.POTENTIAL: []}

# if __name__ == '__main__':
#     """ ------------------- App Start ------------------- """
#     print(NotifyGroup('sell'))
#     print(NotifyGroup('😳 徘徊中：'))
#     print(NotifyGroup.getLineGroup())
#     print(NotifyGroup.getPotentialGroup())
