from enum import Enum


class DailyStock(Enum):
    MARKET_DATE = ("MARKET_DATE", "資料日期")
    STOCK_NAME = ("STOCK_NAME", "證券名稱")
    SYMBOL = ("SYMBOL", "證券代號")
    DEAL_STOCK = ("DEAL_STOCK", "成交股數")
    DEAL_PRICE = ("DEAL_PRICE", "成交金額")
    OPENING_PRICE = ("OPENING_PRICE", "開盤價")
    HIGHEST_PRICE = ("HIGHEST_PRICE", "最高價")
    LOWEST_PRICE = ("LOWEST_PRICE", "最低價")
    CLOSE_PRICE = ("CLOSE_PRICE", "收盤價")
    UPS_AND_DOWNS = ("UPS_AND_DOWNS", "漲跌價差")
    VOLUME = ("VOLUME", "成交筆數")
    CREATETIME = ("CREATETIME", "新增日期")

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
