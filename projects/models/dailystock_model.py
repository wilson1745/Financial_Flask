from sqlalchemy import *

from projects.common.db import db_sqlalchemy
from projects.common.enums.enum_dailystock import DailyStock


class DailyStockModel(db_sqlalchemy.Model):
    __tablename__ = 'DAILYSTOCK'
    marketDate = Column(String(length=20), name=DailyStock.MARKET_DATE.name, primary_key=True, nullable=False)
    stockName = Column(String(length=200), name=DailyStock.STOCK_NAME.name, primary_key=True, nullable=False)
    symbol = Column(String(length=10), name=DailyStock.SYMBOL.name, nullable=False)
    dealStock = Column(Numeric(precision=38), name=DailyStock.DEAL_STOCK.name, nullable=False)
    dealPrice = Column(Numeric(precision=20, scale=3), name=DailyStock.DEAL_PRICE.name)
    openingPrice = Column(Numeric(precision=12, scale=3), name=DailyStock.OPENING_PRICE.name)
    highestPrice = Column(Numeric(precision=12, scale=3), name=DailyStock.HIGHEST_PRICE.name)
    lowestPrice = Column(Numeric(precision=12, scale=3), name=DailyStock.LOWEST_PRICE.name)
    closePrice = Column(Numeric(precision=12, scale=3), name=DailyStock.CLOSE_PRICE.name)
    upsAndDowns = Column(Numeric(precision=12, scale=4), name=DailyStock.UPS_AND_DOWNS.name)
    volume = Column(Numeric(precision=38), name=DailyStock.VOLUME.name, nullable=False)
    createtime = Column(DateTime, name=DailyStock.CREATETIME.name)

    def __init__(self,
                 marketDate, stockName, symbol, dealStock, dealPrice,
                 openingPrice, highestPrice, lowestPrice, closePrice,
                 upsAndDowns, volume, createtime):
        self.marketDate = marketDate
        self.stockName = stockName
        self.symbol = symbol
        self.dealStock = dealStock
        self.dealPrice = dealPrice
        self.openingPrice = openingPrice
        self.highestPrice = highestPrice
        self.lowestPrice = lowestPrice
        self.closePrice = closePrice
        self.upsAndDowns = upsAndDowns
        self.volume = volume
        self.createtime = createtime

    @classmethod
    # @interceptor
    def find_by_symbol(cls, symbol: str):
        try:
            # log.debug(f"get_user name: {name}")
            return cls.query.filter_by(symbol=symbol)
        except Exception as e:
            print(str(e))
