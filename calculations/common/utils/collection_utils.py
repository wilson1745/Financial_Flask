import time

from joblib import parallel_backend, Parallel, delayed

from calculations import LOG
from calculations.common.utils import constants
from calculations.common.utils.constants import CLOSE, DEAL_PRICE, DEAL_STOCK, HIGH, LOW, MARKET_DATE, OPEN, STOCK_NAME, SYMBOL, UPS_AND_DOWNS, \
    VOLUME, HEADERS
from projects.common.constants import THREAD


def arrange_test(header):
    result = ""
    data = str(header)
    if data == "日期":
        result = MARKET_DATE
    elif data == "證券名稱":
        result = STOCK_NAME
    elif data == "證券代號":
        result = SYMBOL
    elif data == "成交股數":
        result = DEAL_STOCK
    elif data == "成交金額":
        result = DEAL_PRICE
    elif data == "開盤價":
        result = OPEN
    elif data == "最高價":
        result = HIGH
    elif data == "最低價":
        result = LOW
    elif data == "收盤價":
        result = CLOSE
    elif data == "漲跌價差":
        result = UPS_AND_DOWNS
    elif data == "成交筆數":
        result = VOLUME

    return result


class CollectionUtils:

    def __init__(self):
        """ Constructor """
        pass

    @staticmethod
    def header_daily_stock(orignal_headers) -> list:
        # with parallel_backend(THREAD, n_jobs=-1):
        #     new_headers = Parallel()(delayed(arrange_test)(header) for header in orignal_headers)

        new_headers = []

        for column in orignal_headers:
            data = str(column)
            if data == "日期":
                new_headers.append(MARKET_DATE)
            elif data == "證券名稱":
                new_headers.append(STOCK_NAME)
            elif data == "證券代號":
                new_headers.append(SYMBOL)
            elif data == "成交股數":
                new_headers.append(DEAL_STOCK)
            elif data == "成交金額":
                new_headers.append(DEAL_PRICE)
            elif data == "開盤價":
                new_headers.append(OPEN)
            elif data == "最高價":
                new_headers.append(HIGH)
            elif data == "最低價":
                new_headers.append(LOW)
            elif data == "收盤價":
                new_headers.append(CLOSE)
            elif data == "漲跌價差":
                new_headers.append(UPS_AND_DOWNS)
            elif data == "成交筆數":
                new_headers.append(VOLUME)

        return new_headers

    @staticmethod
    def convert_date(data_ROC) -> str:
        """因為格式為109/1/1，為民國年，需轉換成西元年"""
        date_arr = data_ROC.split("/")
        new_year = int(date_arr[0]) + 1911
        return f"{new_year}-{date_arr[1]}-{date_arr[2]}"

    @staticmethod
    def header_fund(orignal_headers) -> list:
        new_headers = []

        for column in orignal_headers:
            data = str(column)
            if data == "日期":
                new_headers.append(MARKET_DATE)
            elif data == "證券名稱":
                new_headers.append(STOCK_NAME)
            elif data == "證券代號":
                new_headers.append(SYMBOL)
            elif data == "收盤價":
                new_headers.append(CLOSE)
            elif data == "漲跌價差":
                new_headers.append(UPS_AND_DOWNS)

        return new_headers


if __name__ == '__main__':
    """ ------------------- App Start ------------------- """
    now = time.time()

    try:
        headers = CollectionUtils.header_daily_stock(HEADERS)
        print(headers)
    except Exception:
        raise
    finally:
        LOG.debug(f"Time consuming: {time.time() - now}")
