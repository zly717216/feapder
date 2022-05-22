# -*- coding: utf-8 -*-
"""
Created on 2022-05-16 23:02:57
---------
@summary: 天天基金列表数据爬虫
---------
@author: Administrator
"""

from datetime import datetime

import feapder
from feapder.utils.tools import to_date

from items import *


class TtfundAll(feapder.AirSpider):

    def start_requests(self):

        type_list = ['gp', 'hh', 'zq', 'zs', 'qdii', 'lof', 'fof']
        url = 'http://fund.eastmoney.com/data/rankhandler.aspx'
        headers = {
            'Referer': 'http://fund.eastmoney.com',
        }
        date = str(datetime.now().date())

        for _type in type_list:
            params = {
                'op': 'ph', 'dt': 'kf', 'ft': _type, 'rs': '', 'gs': '0', 'sc': '6yzf',
                'st': 'desc', 'sd': date, 'ed': date, 'qdii': '',
                'tabSubtype': ',,,,,', 'pi': '1', 'pn': '10000', 'dx': '1',
                'v': '0.11025636428963392'
            }
            yield feapder.Request(url, params=params, headers=headers, type=_type)

    def parse(self, request, response):

        data_list = response.re('\"(.*?)\",')
        for i in data_list:

            x = i.split(',')
            item = fund_list_item.FundListItem(**{
                'code': x[0], 'name': x[1], 'establish_date': to_date(x[16], date_format="%Y-%m-%d"),
                'service_charge': x[22], 'type': request.type
            })

            yield item


if __name__ == "__main__":
    TtfundAll().start()
