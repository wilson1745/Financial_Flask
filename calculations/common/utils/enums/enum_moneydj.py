from enum import Enum


class MoneyDj(Enum):
    BASIC = ('yp011000', '基本資料')
    NET_WORTH = ('yp010000', '淨值表')
    PERFORMANCE = ('yp012000', '績效表')
    SHAREHOLDING = ('yp013000', '持股')
    DIVIDEND = ('funddividend', '配息')
    TREND = ('yp081006', '趨勢軌跡')
    EXAMINATION = ('YP016000', '體檢表')
    NEWS = ('YP014000', '相關新聞')
    REPORTS = ('YP015000', '相關報告')
    AWARDS = ('YP017000', '得獎記錄')

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

    def getCaption(self) -> str:
        return self._all_values[0]

    def getValue(self) -> str:
        return self._all_values[1]
