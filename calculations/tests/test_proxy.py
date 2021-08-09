# import scrapy
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
import json
import re


# class ProxyExampleSpider(scrapy.Spider):
class ProxyExampleSpider:
    name = "proxy_example"
    allowed_domains = ["www.us-proxy.org"]
    start_urls = ['http://www.us-proxy.org']

    @classmethod
    def proxy_check_available(cls, response):
        proxy_ip = response.meta['_proxy_ip']
        if proxy_ip == json.loads(response.text)['origin']:
            meta_p = {
                'scheme': response.meta['_proxy_scheme'],
                'proxy': response.meta['proxy'],
                'port': response.meta['port']
            }
            print(meta_p)

    @classmethod
    def parse(cls):
        # response = urlopen('https://free-proxy-list.net/', timeout=600)
        meta = {}

        response = requests.get('https://free-proxy-list.net/', timeout=600)
        soup = BeautifulSoup(response.text, 'lxml')
        trs = soup.select("#proxylisttable tr")
        for tr in trs:
            tds = tr.select("td")
            if len(tds) > 6:
                ip = tds[0].text
                port = tds[1].text
                anonymity = tds[4].text
                ifScheme = tds[6].text
                if ifScheme == 'yes':
                    scheme = 'https'
                else:
                    scheme = 'http'
                proxy = "%s://%s:%s" % (scheme, ip, port)
                meta = {
                    'port': port,
                    'proxy': proxy,
                    'dont_retry': True,
                    'download_timeout': 3,
                    '_proxy_scheme': scheme,
                    '_proxy_ip': ip
                }

                # print(meta)

        response = requests.get('https://httpbin.org/ip', callback=cls.proxy_check_available, meta=meta, dont_filter=True)

    @staticmethod
    def parse2():
        r = requests.get('https://free-proxy-list.net/').text
        s = BeautifulSoup(r, 'lxml')
        print(s)


if __name__ == '__main__':
    ProxyExampleSpider.parse()
    # ProxyExampleSpider.parse2()
