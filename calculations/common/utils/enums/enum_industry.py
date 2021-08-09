from enum import Enum


class IndustryGroup(Enum):
    """ Enum Industry """

    CEMENT = ("11", "水泥")
    FOOD = ("12", "食品")
    FOOD_2 = ("42", "食品")
    PLASTIC = ("13", "塑膠")
    PLASTIC_2 = ("43", "塑膠")
    TEXTILE = ("14", "紡織纖維")
    TEXTILE_2 = ("44", "紡織纖維")
    MECHANICAL = ("15", "電機機械")
    MECHANICAL_2 = ("45", "電機機械")
    ELECTRICAL = ("16", "電器電纜")
    ELECTRICAL_2 = ("46", "電器電纜")
    CHEMICAL = ("17", "化學")
    CHEMICAL_2 = ("47", "化學")
    GLASS = ("18", "玻璃陶瓷")
    GLASS_2 = ("48", "玻璃陶瓷")
    PAPERMAKING = ("19", "造紙")
    STEEL = ("20", "鋼鐵")
    STEEL_2 = ("50", "鋼鐵")
    RUBBER = ("21", "橡膠")
    RUBBER_2 = ("51", "橡膠")
    CAR = ("22", "汽車")
    ELECTRONIC_1 = ("23", "電子資訊")
    ELECTRONIC_2 = ("24", "電子資訊")
    ELECTRONIC_3 = ("30", "電子資訊")
    ELECTRONIC_4 = ("34", "電子資訊")
    ELECTRONIC_5 = ("35", "電子資訊")
    ELECTRONIC_6 = ("36", "電子資訊")
    ELECTRONIC_7 = ("37", "電子資訊")
    ELECTRONIC_8 = ("53", "電子資訊")
    ELECTRONIC_9 = ("54", "電子資訊")
    ELECTRONIC_10 = ("61", "電子資訊")
    ELECTRONIC_11 = ("62", "電子資訊")
    ELECTRONIC_12 = ("64", "電子資訊")
    ELECTRONIC_13 = ("65", "電子資訊")
    ELECTRONIC_14 = ("67", "電子資訊")
    ELECTRONIC_15 = ("80", "電子資訊")
    ELECTRONIC_16 = ("81", "電子資訊")
    ELECTRONIC_17 = ("82", "電子資訊")
    BUILD = ("25", "營建")
    BUILD_2 = ("55", "營建")
    TRANSPORT = ("26", "運輸")
    TRANSPORT_2 = ("56", "運輸")
    SIGHTSEEING = ("27", "觀光")
    SIGHTSEEING_2 = ("57", "觀光")
    FINANCIAL = ("28", "金融保險")
    FINANCIAL_2 = ("58", "金融保險")
    DEPARTMENT_STORE = ("29", "百貨")
    BIOTECHNOLOGY = ("41", "生技醫療")
    INTERNET = ("49", "通訊網路")
    SOFTWARE = ("52", "軟體")
    SECURITIES = ("60", "證券")
    MANAGED_STOCKS = ("87", "管理股票")
    TDR = ("91", "TDR台灣存託憑證")
    COMPREHENSIVE = ("98", "綜合")
    OTHER = ("99", "其他")
    OTHER_2 = ("89", "其他")

    def __new__(cls, *values):
        """ Constructor """
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

    def getCaption(self) -> str:
        return self.all_values[0]

    def getValue(self) -> str:
        return self.all_values[1]

    @classmethod
    def getAllInMaps(cls) -> dict:
        """ Output enums as dictionary """
        ob = {}
        for m in cls:
            # ob[m.value] = 0
            ob[m.all_values[0]] = 0
            # ob[m.all_values[1]] = 0
        return ob

# if __name__ == '__main__':
#     """ ------------------- App Start ------------------- """
#     print(IndustryGroup("29"))
#     print(IndustryGroup("電機機械"))
#     print(IndustryGroup.getAllInMaps())
