# -*- coding: utf-8 -*-
"""
Created on 2022-05-22 19:46:22
---------
@summary:
---------
@author: Administrator
"""

from feapder import Item


class FundNetItem(Item):
    """
    This class was generated by feapder
    command: feapder create -i fund_net 1
    """

    __table_name__ = "fund_net"

    def __init__(self, *args, **kwargs):

        self.code = kwargs.get('code')
        self.date = kwargs.get('date')
        self.net_worth = kwargs.get('net_worth')
        self.pull_back = kwargs.get('pull_back')
        self.range = kwargs.get('range')
        self.replace_day = kwargs.get('replace_day')
