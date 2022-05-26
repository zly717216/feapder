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


class IndexBase(feapder.AirSpider):

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

    def validate(self, request, response):
        """
        @summary: 校验函数, 可用于校验response是否正确
        """
        if response is not None:
            return True

        if response.status_code == 200:
            return True

        return False


if __name__ == "__main__":
    IndexBase().start()
