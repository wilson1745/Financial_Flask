from marshmallow import fields

from projects.common.ma import ma_marshmallow


class DailyStockSchema(ma_marshmallow.Schema):
    marketDate = fields.Str()
    stockName = fields.Str()
    symbol = fields.Str()
    dealStock = fields.Float()
    dealPrice = fields.Float()
    openingPrice = fields.Float()
    highestPrice = fields.Float()
    lowestPrice = fields.Float()
    closePrice = fields.Float()
    upsAndDowns = fields.Float()
    volume = fields.Float()
    createtime = fields.DateTime()
