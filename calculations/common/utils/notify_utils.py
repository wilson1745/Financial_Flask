# -*- coding: UTF-8 -*-
# from multiprocessing import Pool
from multiprocessing.pool import ThreadPool

from pandas import DataFrame

from calculations.common.constants.constants import CLOSE, CLOSE_Y, D, DOWN_EMO, K, K_D, MARKET_DATE, RSI, RSI_Y, SGNL_B, SGNL_S, \
    STOCK_NAME, SYMBOL, UP_EMO, YYYYMMDD, YYYYMMDD_SLASH
from calculations.common.enums.enum_line_notify import NotifyGroup
from calculations.common.enums.enum_notifytok import NotifyTok
from calculations.common.utils.date_utils import DateUtils
from calculations.common.utils.http_utils import HttpUtils
from calculations.core import CPU_THREAD, LOG
from calculations.core.interceptor import interceptor
from calculations.logic import FunctionBollingBand, FunctionKD, FunctionMA, FunctionRSI


class NotifyUtils:
    """ Handle the information for line notify """

    def __init__(self):
        """ Constructor """
        pass

    @staticmethod
    # @interceptor
    def __msg_arrow(value: float) -> str:
        """ Set emoji """
        sym = ''
        if value > 0:
            sym = UP_EMO
        elif value < 0:
            sym = DOWN_EMO
        return f"{sym}{abs(value)}"

    @classmethod
    def __async_lambda(cls, lambda_func, datas):
        """ 使用apply_async搭配lambda functional programming """
        return list(filter(lambda_func, datas))

    @classmethod
    def __gen_industry_row(cls, row) -> str:
        """ 加速度指標的產業數量 """
        rowStr = ''
        rowStr += f"{row[0]}：{row[1]}"
        return rowStr

    @classmethod
    def __gen_str_row(cls, row, tok: NotifyTok) -> str:
        """ 建立每隻股票的格式 """
        rowStr = ''
        # 基金不用顯示Symbol
        rowStr += f"\n名稱：{row[STOCK_NAME]} {'' if tok is NotifyTok.FUNDS else ('(' + row[SYMBOL] + ')')}"
        rowStr += f"\n日期：{DateUtils.str_fmt(row[MARKET_DATE], YYYYMMDD, YYYYMMDD_SLASH)}"
        rowStr += f"\n收盤價：{row[CLOSE]} ({cls.__msg_arrow(row[CLOSE_Y])})"
        # RSI(12)
        rowStr += f"\nRSI：{row[RSI]} ({cls.__msg_arrow(row[RSI_Y])})"
        # KD(9)
        rowStr += f"\nKD：{row[K]}, {row[D]} ({cls.__msg_arrow(row[K_D])})"
        return rowStr

    @staticmethod
    @interceptor
    def __gen_notify_data(df: DataFrame):
        """ Generate indicators (RSI, KD, Bolling, Signal, etc.) """
        if not df.empty:
            """ RSI """
            FunctionRSI.GenRSI(df)

            """ KD """
            FunctionKD.GenKD(df)

            """ Combination of KD and BollingBand (generate trade signal) """
            FunctionBollingBand.GenBollingerBand(df)
            FunctionBollingBand.BuySellSignal(df)

            """ MA cross rate """
            FunctionMA.GetCross(df, 5, 15)

            # Yesterday's CLOSE cross
            df[CLOSE_Y] = (df.iloc[-1][CLOSE] - df.iloc[-2][CLOSE]).round(2)
            # Yesterday's RSI cross
            df[RSI_Y] = (df.iloc[-1][RSI] - df.iloc[-2][RSI]).round(2)
            # KD cross
            df[K_D] = (df.iloc[-1][K] - df.iloc[-1][D]).round(2)
            # 取得當天含有RSI和KD值的最後一筆資料 (row: _iLocIndexer)
            row = df.iloc[-1].copy()

            # Pandas SettingwithCopy 警告解决方案 (https://zhuanlan.zhihu.com/p/41202576)
            # pd.set_option('mode.chained_assignment', None)
            # row_pre: _iLocIndexer = stock.iloc[-2].copy()
            # row['RSI_Y'] = (row[RSI] - row_pre[RSI]).round(2)
            return row
        else:
            return None

    @classmethod
    def __message_send(cls, default_msg, func, rows, lineNotify, token=None):
        """ 統一發送訊息的規格 """
        msg = [default_msg]

        if len(rows) > 0:
            for row in rows:
                # extend => extract whatever types of element inside a list
                msg.extend([func(row) if token is None else func(row, token)])

                # 1000 words limit with Line Notify
                if len(msg) % 9 == 0:
                    lineNotify.send_msg(msg)
                    msg.clear()
                    msg.append(default_msg)

            # Sending the rest data within 1000 words
            if len(msg) > 1:
                lineNotify.send_msg(msg)
        else:
            msg.append("\n無資料...")
            lineNotify.send_msg(msg)

    @classmethod
    @interceptor
    def send_notify(cls, stock_dict: dict, lineNotify: HttpUtils):
        """ 預處理股票格式並送出Line Notify """
        key: NotifyGroup
        for key in stock_dict:
            cls.__message_send(
                f"{DateUtils.default_msg(YYYYMMDD_SLASH)}{key.getValue()}",
                cls.__gen_str_row,
                stock_dict[key],
                lineNotify,
                lineNotify.token)

    @classmethod
    @interceptor
    def send_industry(cls, ind_list: list, lineNotify: HttpUtils):
        """ 重送產業數量的通知 """
        cls.__message_send(
            f"{DateUtils.default_msg(YYYYMMDD_SLASH)}{NotifyGroup.INDEX.getValue()}\n",
            cls.__gen_industry_row,
            ind_list,
            lineNotify)

    @classmethod
    @interceptor
    def arrange_notify(cls, df_list: list = None, stock_dict: dict = None) -> dict:
        """ Generate multiple financial indicators for each product """

        """ Multi-processing pool: https://www.maxlist.xyz/2020/03/20/multi-processing-pool/ """
        # ex: 設定處理程序數量 (pools = Pool(4))
        pools = ThreadPool(CPU_THREAD)
        try:
            if df_list is None:
                LOG.warning("Warning => data_dfs: list = None")
            else:
                results = pools.map(func=cls.__gen_notify_data, iterable=df_list)

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
                        """ Riley's stocks (from http_utils.py) """
                        # 趕快賣
                        stock_dict[NotifyGroup.SELL].extend(
                            pools.apply_async(cls.__async_lambda, (lambda r: r[RSI] >= 70, results)).get())
                        # 好可憐
                        stock_dict[NotifyGroup.BAD].extend(
                            pools.apply_async(cls.__async_lambda, (lambda r: r[RSI] <= 30, results)).get())
                        # 進場做多
                        stock_dict[NotifyGroup.LONG].extend(
                            pools.apply_async(cls.__async_lambda, (lambda r: 70 > r[RSI] > 30 and r[SGNL_B], results)).get())
                        # 進場做空
                        stock_dict[NotifyGroup.SHORT].extend(
                            pools.apply_async(cls.__async_lambda, (lambda r: 70 > r[RSI] > 30 and r[SGNL_S], results)).get())

                        # """ MA cross rate """
                        # # 進場做多
                        # stock_dict[NotifyGroup.LONG].extend(
                        # pools.apply_async(cls.__async_lambda, (lambda r: r[RSI] >= 50 and r[POS] > 0, results)).get())
                        # # 進場做空
                        # stock_dict[NotifyGroup.SHORT].extend(
                        # pools.apply_async(cls.__async_lambda, (lambda r: r[RSI] < 50 and r[POS] < 0, results)).get())

                        # 徘徊不定
                        stock_dict[NotifyGroup.NORMAL].extend(
                            pools.apply_async(cls.__async_lambda, (lambda r: 70 > r[RSI] > 30 and not r[SGNL_B] and not r[SGNL_S], results)).get())

                        pools.close()
                        pools.join()
                    else:
                        """ Portential stocks (from potential_stock.py) """
                        stock_dict[NotifyGroup.POTENTIAL].extend(results)

                    return stock_dict
        except Exception:
            raise
        finally:
            """ 關閉process的pool並等待所有process結束 """
            pools.close()
            # pools.join()
