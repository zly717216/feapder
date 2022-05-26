# -*- coding: utf-8 -*-
"""
Created on 2022-05-16 22:50:52
---------
@summary: 爬虫入口
---------
@author: Administrator
"""

from spiders import ttfund_list
from feapder.utils.custom_argparse import ArgumentParser


def ttfund_all_spider():
    ttfund_list.TtfundList(thread_count=100).start()


# def _baidu_spider2():
#     baidu_spider2.BaiduSpider(thread_count=100, redis_key="baidu_spider").start()


if __name__ == "__main__":

    parser = ArgumentParser(description="天天基金网爬虫")

    parser.add_argument(
        "--ttfund_list", action="store_true", help="轻量爬虫", function=ttfund_all_spider()
    )
    # parser.add_argument(
    #     "--baidu_spider2", action="store_true", help="分布式爬虫", function=_baidu_spider2
    # )

    parser.start()

    # main.py作为爬虫启动的统一入口，提供命令行的方式启动多个爬虫，若只有一个爬虫，可不编写main.py
    # 将上面的xxx修改为自己实际的爬虫名
    # 查看运行命令 python main.py --help
    # AirSpider与Spider爬虫运行方式 python main.py --crawl_xxx
    # BatchSpider运行方式
    # 1. 下发任务：python main.py --crawl_xxx 1
    # 2. 采集：python main.py --crawl_xxx 2
    # 3. 重置任务：python main.py --crawl_xxx 3

