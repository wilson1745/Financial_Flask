from enum import Enum


class IndustryGroup(Enum):
    CEMENT = ("11", "水泥")
    FOOD = ("12", "食品")
    PLASTIC = ("13", "塑膠")
    TEXTILE = ("14", "紡織")
    MECHANICAL = ("15", "電機機械")
    ELECTRICAL = ("16", "電器電纜")
    CHEMICAL = ("17", "化工")
    GLASS = ("18", "玻璃陶瓷")
    PAPERMAKING = ("19", "造紙")
    STEEL = ("20", "鋼鐵")
    RUBBER = ("21", "橡膠")
    CAR = ("22", "汽車")
    ELECTRONIC_1 = ("23", "電子1")
    ELECTRONIC_2 = ("24", "電子2")
    BUILD = ("25", "營建")
    TRANSPORT = ("26", "運輸")
    SIGHTSEEING = ("27", "觀光")
    FINANCIAL = ("28", "金融保險")
    DEPARTMENT_STORE = ("29", "百貨")
    COMPREHENSIVE = ("98", "綜合")
    OTHER = ("99", "其他")

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

    @classmethod
    def __iter__(cls):
        return (cls._member_map_[name] for name in cls._member_names_)

    @classmethod
    def __values__(cls):
        return [m.value for m in cls]

    # @classmethod
    # def getByCaption(cls, caption: str):
    #    return [member for name, member in cls.__members__.items() if member._all_values[0] == caption]

    @classmethod
    def getAllInMaps(cls) -> dict:
        ob = {}
        for m in cls:
            ob[m] = []
        return ob

    # @property
    def getCaption(self) -> str:
        return self._all_values[0]

    # @property
    def getValue(self) -> str:
        return self._all_values[1]

    @classmethod
    def getByValue(cls, value: str):
        return cls[value]

    # @classmethod
    # def getAllGroup(cls) -> dict:
    #     return {cls.SELL: [], cls.LONG: [], cls.SHORT: [], cls.NORMAL: [], cls.BAD: []}

    # @classmethod
    # def getPotentialGroup(cls) -> dict:
    #     return {cls.POTENTIAL: []}
