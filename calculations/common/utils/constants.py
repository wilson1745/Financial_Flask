""" Common """

FILE_ALREADY_EXIST = "File %s already exist"
FILE_NOT_EXIST = "File %s does not exist"
DATA_ALREADY_EXIST = "Data %s already exist"
DATA_NOT_EXIST = "Data %s does not exist"

# TWSE
# ex: https://www.twse.com.tw/exchangeReport/MI_INDEX?response=html&date=20210420&type=ALLBUT0999
TWSE_MI_INDEX = "https://www.twse.com.tw/exchangeReport/MI_INDEX?response=%s&date=%s&type=%s"
TESE_STOCK_DAY_ALL = "http://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL?response=open_data"

# Oracle Client Path
# 先暫時用絕對路徑 => 不然multiprocessing吃不到
ORACLE_CLIENT_PATH = r"/files/instantclient_19_8"
# ORACLE_CLIENT_PATH = "../files/instantclient_19_8"
ORACLE_CLIENT_NETWORK_PATH = ORACLE_CLIENT_PATH + "/network/admin"

# Log Path
LOG_PATH = r"\files\logs\%s.log"
# LOG_PATH = "../files/logs/%s.log"

# TXT Path
URL_ERROR_TXT_PATH = "../files/logs/URLError_%s.txt"

# File Folder Path
HTML_PATH = "../files/scrapy_files/original/html/MI_INDEX_ALLBUT0999_%s.html"
CSV_PATH = "../files/scrapy_files/original/MI_INDEX_ALLBUT0999_%s.csv"
CSV_FINAL_PATH = "../files/scrapy_files/STOCK_DAY_ALL_%s.csv"

# Line Notify
TOKEN_NOTIFY = "kgVHUTkyLWsCfcnMxbsHmsptVPkG5afkZY2NO0I5sDX"
TOKEN_SENSATIONAL = "hlFjUiKkT9jWw1FfnLAVgnwaWJ4CY5DzIg7J33X2vdc"
NOTIFY_LINK = "https://notify-api.line.me/api/notify"
SELL = "sell"
NORMAL = "normal"
BAD = "bad"

# Date Format
YYYYMMDD = "%Y%m%d"
YYYYMMDD_LINE = "%Y-%m-%d"
YYYYMM = "%Y%m"
YYYYMMDD_HHMMSS = "%Y%m%d-%H%M%S"
YYYY_MM_DD = "%Y_%m_%d"
YYYYMMDD_SLASH = "%Y/%m/%d"

# Riley's Stocks
RILEY_STOCKS = ["0050", "0056", "00881", "1802", "2303", "2330", "2324", "2375", "2401", "2441", "2617", "3231", "6116"]
# RILEY_STOCKS = ["020008", "1312A", "1316", "1419", "1459", "1538", "1603", "1713", "2207", "2849", "2851", "2887", "2908", "3026", "3701", "4148",
#                 "4426", "5876", "6172", "9110", "911616"]

# DailyStock
MARKET_DATE = 'market_date'
STOCK_NAME = 'stock_name'
SYMBOL = 'symbol'
DEAL_STOCK = 'deal_stock'
DEAL_PRICE = 'deal_price'
OPENING_PRICE = 'opening_price'
HIGHEST_PRICE = 'highest_price'
LOWEST_PRICE = 'lowest_price'
CLOSE_PRICE = 'close_price'
UPS_AND_DOWNS = 'ups_and_downs'
VOLUME = 'volume'
CREATETIME = 'createtime'

POS = 'POS'
RSI = 'RSI'
RSI_Y = 'RSI_Y'
K = 'K'
D = 'D'
K_D = 'K_D'

OPEN = 'open'
HIGH = 'high'
LOW = 'low'
CLOSE = 'close'

# DailyStock headers
HEADERS = ["日期", "證券代號", "證券名稱", "成交股數", "成交筆數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌價差"]
HEADERS_T = [MARKET_DATE, STOCK_NAME, SYMBOL, DEAL_STOCK, DEAL_PRICE, OPENING_PRICE, HIGHEST_PRICE, LOWEST_PRICE, CLOSE_PRICE, UPS_AND_DOWNS,
             VOLUME, CREATETIME]

SUCCESS = "%s 成功"
FAIL = "%s 失敗"
