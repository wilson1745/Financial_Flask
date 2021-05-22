from sqlalchemy import *

from projects.common.db import db_sqlalchemy


class DailyStockModel(db_sqlalchemy.Model):
    __tablename__ = 'DAILYSTOCK'
    marketDate = Column(String(length=20), primary_key=True, nullable=False)
    stockName = Column(String(length=200), primary_key=True, nullable=False)
    symbol = Column(String(length=10), nullable=False)
    dealStock = Column(Numeric(precision=38), nullable=False)
    dealPrice = Column(Numeric(precision=20, scale=3))
    openingPrice = Column(Numeric(precision=12, scale=3))
    highestPrice = Column(Numeric(precision=12, scale=3))
    lowestPrice = Column(Numeric(precision=12, scale=3))
    closePrice = Column(Numeric(precision=12, scale=3))
    upsAndDowns = Column(Numeric(precision=12, scale=4))
    volume = Column(Numeric(precision=38), nullable=False)
    createtime = Column(DateTime)

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
        # self.upsAndDowns = upsAndDowns
        self.volume = volume
        # self.createtime = createtime
