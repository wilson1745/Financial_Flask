import urllib.parse

url = urllib.parse.unquote(
    'https://fund.cnyes.com/detail/%25E5%2585%2583%25E5%25A4%25A7%25E5%258F%25B0%25E7%2581%25A3%25E9%25AB%2598%25E8%2582%25A1%25E6%2581%25AFETF'
    '%25E9%2580%25A3%25E7%25B5%2590%25E5%259F%25BA%25E9%2587%2591-%25E6%2596%25B0%25E5%258F%25B0%25E5%25B9%25A3('
    'B)%25E9%2585%258D%25E6%2581%25AF/A1b6ByR/shareholding',
    encoding='utf-8', errors='replace')
print(url)

url2 = urllib.parse.unquote(url, encoding='utf-8', errors='replace')
print(url2)

url3 = urllib.parse.quote("元大台灣高股息ETF連結基金-新台幣(B)配息", encoding='utf-8', errors='replace')
print(url3)
