import traceback

from calculations.common.utils.exceptions.core_exception import CoreException
from calculations.core.Interceptor import interceptor
from calculations.repository import dailystock_repo


@interceptor
def main_start():
    """ ------------------- App Start ------------------- """
    try:
        symbol = "2330"
        data = dailystock_repo.findBySymbol(symbol)
        data.drop('market_date', axis=1, inplace=True)
        # print(data.head())

        df = data.copy()
        MA_5 = df.rolling(5).mean()
        MA_20 = df.rolling(20).mean()
        MA_5.dropna(inplace=True)
        # print(MA_5.head(10))
        # print(MA_5)
        # print(MA_20)

    except Exception as e:
        CoreException.show_error(e, traceback.format_exc())


if __name__ == '__main__':
    main_start()
    print("====== End of program ======")
