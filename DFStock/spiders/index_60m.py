# -*- coding: utf-8 -*-
"""
Created on 2022-05-23 00:10:48
---------
@summary:
---------
@author: Administrator
"""

import time

import feapder
from feapder.utils.tools import jsonp2json

from index_base import IndexBase


class Index60M(IndexBase):

    def parse(self, request, response):

        # target: https://quote.eastmoney.com/concept/sh113638.html
        json_data = jsonp2json(response.text)['data']
        code_list = [{
            'code': i['f12'], 'market': i['f13'], 'name': i['f14']
        } for i in json_data['diff'] if json_data]

        for i in code_list:

            url = 'http://push2his.eastmoney.com/api/qt/stock/kline/get'
            params = {
                'fields1': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13',
                'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                'beg': '0',
                'end': '20500101',
                'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                'rtntype': '6',
                'secid': f'{i["market"]}.{i["code"]}',
                'klt': '60',
                'fqt': '0',
                'cb': f'jsonp{int(time.time() * 1000)}'
            }

            yield feapder.Request(
                url, params=params, callback=self.parse_kline,
                period='60m', type='index'
            )


if __name__ == "__main__":
    Index60M().start()
