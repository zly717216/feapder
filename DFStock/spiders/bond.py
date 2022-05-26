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


class Bond(feapder.AirSpider):

    def start_requests(self):

        t = int(time.time() * 1000)

        # target: https://data.eastmoney.com/kzz/default.html
        url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
        params = {
            'callback': f'jQuery1123011094267134428404_{t}', 'sortColumns': 'PUBLIC_START_DATE', 'sortTypes': '-1',
            'pageSize': '1000',
            'pageNumber': '1',
            'reportName': 'RPT_BOND_CB_LIST',
            'columns': 'ALL',
            'quoteColumns': 'f2~01~CONVERT_STOCK_CODE~CONVERT_STOCK_PRICE,f235~10~SECURITY_CODE~TRANSFER_PRICE,f236~'
                            '10~SECURITY_CODE~TRANSFER_VALUE,f2~10~SECURITY_CODE~CURRENT_BOND_PRICE,f237~10~SECURITY'
                            '_CODE~TRANSFER_PREMIUM_RATIO,f239~10~SECURITY_CODE~RESALE_TRIG_PRICE,f240~10~SECURITY_C'
                            'ODE~REDEEM_TRIG_PRICE,f23~01~CONVERT_STOCK_CODE~PBV_RATIO',
            'source': 'WEB',
            'client': 'WEB'
        }

        yield feapder.Request(url, params=params)

    def parse(self, request, response):

        # target: https://quote.eastmoney.com/concept/sh113638.html
        json_data = jsonp2json(response.text)['result']
        code_list = [{
            'name': i['SECURITY_NAME_ABBR'], 'code': i['SECURITY_CODE'],
            'market': 0 if i['SECUCODE'][-2:] == 'SZ' else 1
        } for i in json_data['data']]

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
                    type='bond'
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
                    item = bond_item.Bond1DItem(**data)
                elif period == '1m':
                    item = bond_item.Bond1MItem(**data)
                elif period == '5m':
                    item = bond_item.Bond5MItem(**data)
                elif period == '15m':
                    item = bond_item.Bond15MItem(**data)
                elif period == '30m':
                    item = bond_item.Bond30MItem(**data)
                elif period == '60m':
                    item = bond_item.Bond60MItem(**data)
                elif period == '120m':
                    item = bond_item.Bond120MItem(**data)
                else:
                    item = None

                yield item


if __name__ == "__main__":
    Bond().start()
