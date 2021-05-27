import logging

from projects.common.constants import LOG_PROJECTS

log = logging.getLogger(LOG_PROJECTS)


class CollectionUtils:

    @staticmethod
    def create_new_header(orignal_headers) -> list:
        new_headers = []

        for column in orignal_headers:
            data = str(column)
            if data == "日期":
                new_headers.append("trade_date")
            elif data == "證券名稱":
                new_headers.append("stock_name")
            elif data == "成交股數":
                new_headers.append("volume")
            elif data == "成交金額":
                new_headers.append("total_price")
            elif data == "開盤價":
                new_headers.append("open")
            elif data == "最高價":
                new_headers.append("high")
            elif data == "最低價":
                new_headers.append("low")
            elif data == "收盤價":
                new_headers.append("close")
            elif data == "漲跌價差":
                new_headers.append("spread")
            elif data == "成交筆數":
                new_headers.append("transactions_number")

        return new_headers

    @staticmethod
    def create_old_header(orignal_headers) -> list:
        new_headers = []

        for column in orignal_headers:
            data = str(column)
            if data == "證券代號":
                new_headers.append("stock_symbol")
            elif data == "證券名稱":
                new_headers.append("stock_name")
            elif data == "成交股數":
                new_headers.append("volume")
            elif data == "成交金額":
                new_headers.append("total_price")
            elif data == "開盤價":
                new_headers.append("open")
            elif data == "最高價":
                new_headers.append("high")
            elif data == "最低價":
                new_headers.append("low")
            elif data == "收盤價":
                new_headers.append("close")
            elif data == "漲跌價差":
                new_headers.append("spread")
            elif data == "成交筆數":
                new_headers.append("transactions_number")

        return new_headers

    @staticmethod
    def header_daily_stock(orignal_headers) -> list:
        new_headers = []

        for column in orignal_headers:
            data = str(column)
            if data == "日期":
                new_headers.append("market_date")
            elif data == "證券名稱":
                new_headers.append("stock_name")
            elif data == "證券代號":
                new_headers.append("symbol")
            elif data == "成交股數":
                new_headers.append("deal_stock")
            elif data == "成交金額":
                new_headers.append("deal_price")
            elif data == "開盤價":
                new_headers.append("opening_price")
            elif data == "最高價":
                new_headers.append("highest_price")
            elif data == "最低價":
                new_headers.append("lowest_price")
            elif data == "收盤價":
                new_headers.append("close_price")
            elif data == "漲跌價差":
                new_headers.append("ups_and_downs")
            elif data == "成交筆數":
                new_headers.append("volume")

        return new_headers

    @staticmethod
    def convert_date(data_ROC) -> str:
        """因為格式為109/1/1，為民國年，需轉換成西元年"""
        date_arr = data_ROC.split("/")
        new_year = int(date_arr[0]) + 1911

        return f"{new_year}-{date_arr[1]}-{date_arr[2]}"

    @staticmethod
    def print_data(date, stock_data):
        log.debug("",
                  stock_data.stock_symbol,
                  date,
                  stock_data.open,
                  stock_data.high,
                  stock_data.low,
                  stock_data.close,
                  int(stock_data.volume.replace(",", "")),
                  date)
