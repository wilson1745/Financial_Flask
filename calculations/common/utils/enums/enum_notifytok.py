from enum import Enum


class NotifyTok(Enum):
    MINE = ("個人", 'kgVHUTkyLWsCfcnMxbsHmsptVPkG5afkZY2NO0I5sDX')
    RILEY = ("Riley", 'hlFjUiKkT9jWw1FfnLAVgnwaWJ4CY5DzIg7J33X2vdc')
    FUNDS = ("基金", '38rUaL90s5WlYdMwGTM1YKOQo69ZXBODzboJRmEr4aE')

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
