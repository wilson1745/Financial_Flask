# -*- coding: UTF-8 -*-
import multiprocessing
# from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

from pandas import DataFrame

from calculations import log
from calculations.common.utils.constants import CLOSE, CLOSE_Y, D, DOWN_EMO, K, K_D, MARKET_DATE, RSI, RSI_Y, SGNL_B, SGNL_S, STOCK_NAME, SYMBOL, \
    UP_EMO, UPS_AND_DOWNS, UPS_AND_DOWNS_PCT, YYYYMMDD, YYYYMMDD_SLASH
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.enums.enum_line_notify import NotifyGroup
from calculations.common.utils.enums.enum_notifytok import NotifyTok
from calculations.core.Interceptor import interceptor
from calculations.logic import FunctionBollingBand, FunctionKD, FunctionMA, FunctionRSI
from calculations.common.utils.line_utils import LineUtils


class NotifyUtils:
    """ TODO description """

    def __init__(self):
        """ Constructor """
        pass

    @staticmethod
    # @interceptor
    def __msg_arrow(value: float) -> str:
        """ TODO description """
        sym = ''
        if value > 0:
            sym = UP_EMO
        elif value < 0:
            sym = DOWN_EMO
        return f"{sym}{abs(value)}"

    @classmethod
    # @interceptor
    def __genIndustryRow(cls, row) -> str:
        """ TODO description """
        rowStr = ''
        rowStr += f"\n指數：{row[SYMBOL]}"
        rowStr += f"\n日期：{DateUtils.strformat(row[MARKET_DATE], YYYYMMDD, YYYYMMDD_SLASH)}"
        rowStr += f"\n收盤指數：{row[CLOSE]}"
        rowStr += f"\n漲跌點數：{cls.__msg_arrow(row[UPS_AND_DOWNS])}"
        rowStr += f"\n漲跌百分比(%)：{cls.__msg_arrow(row[UPS_AND_DOWNS_PCT])}%"
        return rowStr

    @classmethod
    # @interceptor
    def __gen_str_row(cls, row, tok: NotifyTok) -> str:
        """ 建立每隻股票的格式 """
        # row = row.drop(labels=[SYMBOL])
        rowStr = ''
        # 基金不用顯示Symbol
        rowStr += f"\n名稱：{row[STOCK_NAME]} {'' if tok is NotifyTok.FUNDS else ('(' + row[SYMBOL] + ')')}"
        rowStr += f"\n日期：{DateUtils.strformat(row[MARKET_DATE], YYYYMMDD, YYYYMMDD_SLASH)}"
        rowStr += f"\n收盤價：{row[CLOSE]} ({cls.__msg_arrow(row[CLOSE_Y])})"
        # RSI(12)
        rowStr += f"\nRSI：{row[RSI]} ({cls.__msg_arrow(row[RSI_Y])})"
        # KD(9)
        rowStr += f"\nKD：{row[K]}, {row[D]} ({cls.__msg_arrow(row[K_D])})"
        return rowStr

    @staticmethod
    @interceptor
    def __gen_notify_data(df: DataFrame):
        """ TODO description """
        if not df.empty:
            """ RSI """
            FunctionRSI.GenRSI(df)

            """ KD """
            FunctionKD.GenKD(df)

            """ Combination of KD and BollingBand (generate trade signal) """
            FunctionBollingBand.GenBollingerBand(df)
            FunctionBollingBand.BuySellSignal(df)

            """ MA cross rate """
            stock = FunctionMA.GetCross(df, 5, 15)

            # Yesterday's CLOSE cross
            stock[CLOSE_Y] = (stock.iloc[-1][CLOSE] - stock.iloc[-2][CLOSE]).round(2)
            # Yesterday's RSI cross
            stock[RSI_Y] = (stock.iloc[-1][RSI] - stock.iloc[-2][RSI]).round(2)
            # KD cross
            stock[K_D] = (stock.iloc[-1][K] - stock.iloc[-1][D]).round(2)
            # 取得當天含有RSI和KD值的最後一筆資料 (row: _iLocIndexer)
            row = stock.iloc[-1].copy()

            # Pandas SettingwithCopy 警告解决方案 (https://zhuanlan.zhihu.com/p/41202576)
            # pd.set_option('mode.chained_assignment', None)
            # row_pre: _iLocIndexer = stock.iloc[-2].copy()
            # row['RSI_Y'] = (row[RSI] - row_pre[RSI]).round(2)

            return row
        else:
            return None

    @classmethod
    @interceptor
    def send_notify(cls, stock_dict: dict, lineNotify: LineUtils):
        """ 預處理股票格式並送出Line Notify """
        # TODO pool = multiprocessing.Pool(4)
        # TODO out1, out2, out3 = zip(*pool.map(calc_stuff, range(0, 10 * offset, offset)))

        key: NotifyGroup
        for key in stock_dict:
            default = f"{DateUtils.default_msg(YYYYMMDD_SLASH)}{key.getValue()}"
            msg = [default]

            if len(stock_dict[key]) > 0:
                for row in stock_dict[key]:
                    # extend => extract whatever types of element inside a list
                    msg.extend([cls.__gen_str_row(row, lineNotify.token)])

                    # 1000 words limit with Line Notify
                    if len(msg) % 9 == 0:
                        lineNotify.send_msg(msg)
                        msg.clear()
                        msg.append(default)

                # Sending the rest data within 1000 words
                if len(msg) > 1:
                    lineNotify.send_msg(msg)
            else:
                msg.append("\n無資料...")
                lineNotify.send_msg(msg)

    @classmethod
    @interceptor
    def send_industry(cls, df: DataFrame, lineNotify: LineUtils):
        """ TODO description """
        default = f"{DateUtils.default_msg(YYYYMMDD_SLASH)}{NotifyGroup.INDEX.getValue()}"
        msg = [default]

        if not df.empty:
            for index, row in df.iterrows():
                # FIXME 暫定漲跌百分比 > 0的資料
                if row[UPS_AND_DOWNS_PCT] > 0:
                    # extend => extract whatever types of element inside a list
                    msg.extend([cls.__genIndustryRow(row)])

                    # 1000 words limit with Line Notify
                    if len(msg) % 9 == 0:
                        lineNotify.send_msg(msg)
                        msg.clear()
                        msg.append(default)

            # Sending the rest data within 1000 words
            if len(msg) > 1:
                lineNotify.send_msg(msg)
        else:
            msg.append("\n無資料...")
            lineNotify.send_msg(msg)

    @classmethod
    @interceptor
    def arrange_notify(cls, df_list: list = None, stock_dict: dict = None) -> dict:
        """ Generate multiple financial indicators for each product """
        """ Multi-processing pool: https://www.maxlist.xyz/2020/03/20/multi-processing-pool/ """
        # ex: 設定處理程序數量 (pools = Pool(4))
        pools = ThreadPool(multiprocessing.cpu_count() - 1)

        try:
            if df_list is None:
                log.warning("Warning => data_dfs: list = None")
            else:
                results = pools.map(func=cls.__gen_notify_data, iterable=df_list)
                # results = list(filter(None, results))

                # results = pools.starmap_async(genNotifyData,
                #                                      zip(dfs, repeat(pool)),
                #                                      callback=CoreException.show,
                #                                      error_callback=CoreException.show_error)

                # results = pools.map_async(func=genNotifyData,
                #                                  iterable=dfs,
                #                                  callback=CoreException.show,
                #                                  error_callback=CoreException.error)

                # 包含Key資料的dictionary
                if len(results) > 0:
                    if not NotifyGroup.POTENTIAL in stock_dict:
                        """ Riley's stocks (from line_utils.py) """
                        for row in results:
                            print(row)
                            if (row[RSI]) >= 70:
                                # 趕快賣
                                stock_dict[NotifyGroup.SELL].append(row)
                            elif row[RSI] <= 30:
                                # 好可憐
                                stock_dict[NotifyGroup.BAD].append(row)
                            else:
                                """ KD, BollingBand """
                                if row[SGNL_B]:
                                    # 進場做多
                                    stock_dict[NotifyGroup.LONG].append(row)
                                elif row[SGNL_S]:
                                    # 進場做空
                                    stock_dict[NotifyGroup.SHORT].append(row)

                                # """ MA cross rate """
                                # if row[RSI] >= 50 and row[POS] > 0:
                                #     # 進場做多
                                #     stockDict[NotifyGroup.LONG].append(row)
                                # elif row[RSI] < 50 and row[POS] < 0:
                                #     # 進場做空
                                #     stockDict[NotifyGroup.SHORT].append(row)

                                else:
                                    # 徘徊不定
                                    stock_dict[NotifyGroup.NORMAL].append(row)
                    else:
                        """ Portential stocks (from potential_stock.py) """
                        for row in results:
                            stock_dict[NotifyGroup.POTENTIAL].append(row)

                    return stock_dict
        except Exception:
            raise
        finally:
            """ 關閉process的pool並等待所有process結束 """
            pools.close()
            # pools.join()
