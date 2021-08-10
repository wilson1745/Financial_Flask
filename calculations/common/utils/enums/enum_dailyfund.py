from enum import Enum


class FundGroup(Enum):
    DAILY = ("daily", "單日")
    RANGE = ("range", "週期")

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
