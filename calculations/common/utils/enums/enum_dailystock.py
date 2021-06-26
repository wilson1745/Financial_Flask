from enum import Enum


class DailyStock(Enum):
    MARKET_DATE = ("market_date", "日期")
    STOCK_NAME = ("stock_name", "證券名稱")
    SYMBOL = ("symbol", "證券代號")
    DEAL_STOCK = ("deal_stock", "成交股數")
    DEAL_PRICE = ("deal_price", "成交金額")
    OPENING_PRICE = ("opening_price", "開盤價")
    HIGHEST_PRICE = ("highest_price", "最高價")
    LOWEST_PRICE = ("lowest_price", "最低價")
    CLOSE_PRICE = ("close_price", "收盤價")
    UPS_AND_DOWNS = ("ups_and_downs", "漲跌價差")
    VOLUME = ("volume", "成交筆數")
    CREATETIME = ("createtime", "新增日期")

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
