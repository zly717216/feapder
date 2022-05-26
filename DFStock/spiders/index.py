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
from feapder.utils.tools import jsonp2json, to_date

from items import *


class Index(feapder.AirSpider):

    def start_requests(self):

        t = int(time.time() * 1000)

        # target: http://quote.eastmoney.com/center/gridlist.html#index_sh
        # target: http://quote.eastmoney.com/center/gridlist.html#index_sz
        # target: http://quote.eastmoney.com/center/gridlist.html#index_components
        # target: http://quote.eastmoney.com/center/gridlist.html#index_zzzs

        url = 'http://76.push2.eastmoney.com/api/qt/clist/get'
        fs_list = ['m:1', 'm:0 t:5', 'm:1 s:3,m:0 t:5', 'm:2']

        for fs in fs_list:
            params = {
                'cb': f'jQuery112409104298785094747_{t}',
                'pn': '1',
                'pz': '1000',
                'po': '1',
                'np': '1',
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': '2',
                'invt': '2',
                'wbp2u': '|0|0|0|web',
                'fid': 'f3',
                'fs': fs,
                's': '2',
                'fields': 'f12,f13,f14',
                '_': t
            }

            yield feapder.Request(url, params=params)

    def parse(self, request, response):

        # target: https://quote.eastmoney.com/concept/sh113638.html
        json_data = jsonp2json(response.text)['data']
        code_list = [{
            'code': i['f12'], 'market': i['f13'], 'name': i['f14']
        } for i in json_data['diff'] if json_data]

        for i in code_list:

            url = 'http://push2his.eastmoney.com/api/qt/stock/kline/get'
            # 构造 1d、1m、5m、15m、30m、60m、120m K 线请求
            klt_list = ['101', '1', '5', '15', '30', '60', '120']

            for klt in klt_list:
                params = {
                    'fields1': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13',
                    'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
                    'beg': '0',
                    'end': '20500101',
                    'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
                    'rtntype': '6',
                    'secid': f'{i["market"]}.{i["code"]}',
                    'klt': klt,
                    'fqt': '0',
                    'cb': f'jsonp{int(time.time() * 1000)}'
                }

                yield feapder.Request(
                    url, params=params, callback=self.parse_kline,
                    period='1d' if klt == '101' else klt + 'm',
                    type='index'
                )

    def parse_kline(self, request, response):

        json_data = jsonp2json(response.text)['data']
        if json_data:

            code = json_data['code']
            name = json_data['name']
            market = json_data['market']
            pre_close = json_data['prePrice']
            period = request.period
            _type = request.type

            for i in json_data['klines']:

                _datetime, _open, close, high, low, volume, amount, amplitude, \
                _range, range_money, turnover = i.split(',')

                if period == '1d':
                    _datetime = to_date(_datetime, date_format="%Y-%m-%d")
                else:
                    _datetime = to_date(_datetime, date_format="%Y-%m-%d %H:%M")

                data = {
                    'code': code, 'name': name, 'market': market, 'pre_close': pre_close,
                    'datetime': _datetime, 'open': _open, 'close': close, 'high': high,
                    'low': low, 'volume': volume, 'amount': amount, 'amplitude': amplitude,
                    'range': _range, 'range_money': range_money, 'turnover': turnover,
                    'period': period, 'type': _type
                }

                if period == '1d':
                    item = index_item.Index1DItem(**data)
                elif period == '1m':
                    item = index_item.Index1MItem(**data)
                elif period == '5m':
                    item = index_item.Index5MItem(**data)
                elif period == '15m':
                    item = index_item.Index15MItem(**data)
                elif period == '30m':
                    item = index_item.Index30MItem(**data)
                elif period == '60m':
                    item = index_item.Index60MItem(**data)
                elif period == '120m':
                    item = index_item.Index120MItem(**data)
                else:
                    item = None

                yield item


if __name__ == "__main__":
    Index().start()
