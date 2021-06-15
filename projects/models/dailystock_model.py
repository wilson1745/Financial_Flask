from sqlalchemy import *

from projects.common.db import db_sqlalchemy
from projects.common.enums.enum_dailystock import DailyStock


class DailyStockModel(db_sqlalchemy.Model):
    __tablename__ = 'DAILYSTOCK'
    market_date = Column(String(length=20), name=DailyStock.MARKET_DATE.name, primary_key=True, nullable=False)
    stock_name = Column(String(length=200), name=DailyStock.STOCK_NAME.name, primary_key=True, nullable=False)
    symbol = Column(String(length=10), name=DailyStock.SYMBOL.name, nullable=False)
    deal_stock = Column(Numeric(precision=38), name=DailyStock.DEAL_STOCK.name, nullable=False)
    deal_price = Column(Numeric(precision=20, scale=3), name=DailyStock.DEAL_PRICE.name)
    opening_price = Column(Numeric(precision=12, scale=3), name=DailyStock.OPENING_PRICE.name)
    highest_price = Column(Numeric(precision=12, scale=3), name=DailyStock.HIGHEST_PRICE.name)
    lowest_price = Column(Numeric(precision=12, scale=3), name=DailyStock.LOWEST_PRICE.name)
    close_price = Column(Numeric(precision=12, scale=3), name=DailyStock.CLOSE_PRICE.name)
    ups_and_downs = Column(Numeric(precision=12, scale=4), name=DailyStock.UPS_AND_DOWNS.name)
    volume = Column(Numeric(precision=38), name=DailyStock.VOLUME.name, nullable=False)
    createtime = Column(DateTime, name=DailyStock.CREATETIME.name)

    def __init__(self,
                 marketDate, stockName, symbol, dealStock, dealPrice,
                 openingPrice, highestPrice, lowestPrice, closePrice,
                 upsAndDowns, volume, createtime):
        self.market_date = marketDate
        self.stock_name = stockName
        self.symbol = symbol
        self.deal_stock = dealStock
        self.deal_price = dealPrice
        self.opening_price = openingPrice
        self.highest_price = highestPrice
        self.lowest_price = lowestPrice
        self.close_price = closePrice
        self.ups_and_downs = upsAndDowns
        self.volume = volume
        self.createtime = createtime

    @classmethod
    # @interceptor
    def find_by_symbol(cls, symbol: str):
        try:
            # log.debug(f'get_user name: {name}')
            return cls.query.filter_by(symbol=symbol).order_by(asc(cls.market_date))
        except Exception as e:
            print(str(e))
