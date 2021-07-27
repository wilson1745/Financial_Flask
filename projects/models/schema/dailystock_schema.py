from marshmallow import fields

from projects.common.ma import ma_marshmallow


class DailyStockSchema(ma_marshmallow.Schema):
    class Meta:
        ordered = True

    market_date = fields.Str()
    stock_name = fields.Str()
    symbol = fields.Str()
    deal_stock = fields.Float()
    deal_price = fields.Float()
    open = fields.Float()
    high = fields.Float()
    low = fields.Float()
    close = fields.Float()
    ups_and_downs = fields.Float()
    volume = fields.Float()
    createtime = fields.DateTime()
