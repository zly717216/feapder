# -*- coding: utf-8 -*-
"""
Created on 2022-05-22 16:42:27
---------
@summary:
---------
@author: Administrator
"""

import feapder


class Baidu(feapder.AirSpider):
    def start_requests(self):
        yield feapder.Request("https://www.baidu.com")

    def parse(self, request, response):
        print("网站地址: ", response.url)


if __name__ == "__main__":
    Baidu().start()