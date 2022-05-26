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
from feapder.utils.log import log
from feapder.utils.tools import to_date, timestamp_to_date

from items import *


class TtfundList(feapder.AirSpider):

    def start_requests(self):
        """
            下发新的请求
            @target: http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;s6yzf;pn50;ddesc;qsd20210520;qed20220520;qdii;zq;gg;gzbd;gzfs;bbzt;sfbb
        """

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
            yield feapder.Request(url, params=params, headers=headers, type=_type, timeout=30)

    def parse(self, request, response):
        """解析基金列表数据"""

        data_list = response.re('\"(.*?)\",')
        for i in data_list:

            x = i.split(',')
            item = fund_list_item.FundListItem(**{
                'code': x[0], 'name': x[1], 'establish_date': to_date(x[16], date_format="%Y-%m-%d"),
                'service_charge': x[22], 'type': request.type
            })

            # @target: http://fund.eastmoney.com/162719.html
            net_url = f'http://fund.eastmoney.com/pingzhongdata/{item.code}.js'
            # @target: http://fundf10.eastmoney.com/gmbd_162719.html
            data_url = f'http://fundf10.eastmoney.com/FundArchivesDatas.aspx'

            net_params = {'v': '20220522155033'}
            scale_params = {
                'type': 'gmbd', 'mode': '0', 'code': item.code, 'rt': '0.9340738728175353'
            }
            struct_params = {'type': 'cyrjg', 'code': item.code, 'rt': '0.1986390887427607'}

            yield item
            yield feapder.Request(net_url, params=net_params, callback=self.parse_net, code=item.code, timeout=30)
            yield feapder.Request(data_url, params=scale_params, callback=self.parse_scale, code=item.code, timeout=30)
            yield feapder.Request(data_url, params=struct_params, callback=self.parse_struct, code=item.code, timeout=30)

    def parse_net(self, request, response):
        """解析净值数据"""

        test = response.re("Data_netWorthTrend = (.*?);")

        try:
            data_list = eval(test[0]) if test else '[]'
            for i in data_list:
                item = fund_net_item.FundNetItem(**{
                    'date': timestamp_to_date(i['x'] // 1000, time_format="%Y-%m-%d"),
                    'net_worth': i['y'],
                    'code': request.code
                })
                yield item
        except Exception as e:
            log.error(e)

    def parse_scale(self, request, response):
        """解析规模数据"""

        tr_list = response.xpath("//table/tbody/tr")
        for tr in tr_list:

            date_str = tr.xpath('./td[1]/text()').extract_first()
            if date_str[0].isdigit():
                item = fund_scale_item.FundScaleItem(**{
                    'date': to_date(date_str, date_format="%Y-%m-%d"),
                    'code': request.code,
                    'apply': tr.xpath('./td[2]/text()').extract_first(),
                    'redeem': tr.xpath('./td[3]/text()').extract_first(),
                    'total': tr.xpath('./td[4]/text()').extract_first(),
                    'scale': tr.xpath('./td[5]/text()').extract_first(),
                    'change_rate': tr.xpath('./td[6]/text()').extract_first()
                })
                yield item
            else:
                break

    def parse_struct(self, request, response):
        """解析持有人结构数据"""

        tr_list = response.xpath("//table/tbody/tr")
        for tr in tr_list:

            date_str = tr.xpath('./td[1]/text()').extract_first()
            if date_str[0].isdigit():
                item = fund_struct_item.FundStructItem(**{
                    'date': to_date(tr.xpath('./td[1]/text()').extract_first(), date_format="%Y-%m-%d"),
                    'code': request.code,
                    'institutional_hold': tr.xpath('./td[2]/text()').extract_first(),
                    'individual_hold': tr.xpath('./td[3]/text()').extract_first(),
                    'inner_hold': tr.xpath('./td[4]/text()').extract_first(),
                    'total': tr.xpath('./td[5]/text()').extract_first(),
                })
                yield item
            else:
                break

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
    TtfundList().start()
