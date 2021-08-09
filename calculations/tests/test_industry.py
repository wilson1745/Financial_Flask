import pandas as pd

pd.set_option("display.width", None)
pd.set_option('display.max_colwidth', None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.unicode.ambiguous_as_wide", True)
pd.set_option("display.unicode.east_asian_width", True)

twseurl = 'https://isin.twse.com.tw/isin/C_public.jsp?strMode=2'

# output parameters
outputFolder = ''  # output folder name
twseFile = 'TWSE.txt'  # output file name

# read_html
twsedf = pd.read_html(twseurl, encoding="Big5")


def getTWSE():
    # open file
    fp = open(outputFolder + twseFile, "a")
    print(twsedf)

    # for str in twsedf[0][0]:
    #     encodeStr = str.encode('utf-8')
    #     strArray = encodeStr.split('')
    #     if len(strArray) == 2:
    #         print(strArray[0], strArray[1])
    #         # write to output file
    #         if len(strArray[0]) == 4:
    #             fp.writelines(strArray[0] + " " + strArray[1] + "\n")
    #
    # fp.close()


getTWSE()
