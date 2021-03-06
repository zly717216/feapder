# -*- coding: utf-8 -*-
"""
Created on 2022-05-22 22:36:14
---------
@summary:
---------
@author: Administrator
"""

from feapder import Item


class FundStructItem(Item):
    """
    This class was generated by feapder
    command: feapder create -i fund_struct 1
    """

    __table_name__ = "fund_struct"

    def __init__(self, *args, **kwargs):

        self.code = kwargs.get('code')
        self.date = kwargs.get('date')
        self.individual_hold = kwargs.get('individual_hold')         # 个人持有
        self.inner_hold = kwargs.get('inner_hold')                   # 内部持有
        self.institutional_hold = kwargs.get('institutional_hold')   # 机构持有
        self.total = kwargs.get('total')                             # 总份额

    def pre_to_db(self):
        """
        入库前的处理
        """

        # 如果有控格，则去除空格
        self.individual_hold = self.individual_hold.strip() if self.individual_hold else self.individual_hold
        self.inner_hold = self.inner_hold.strip() if self.inner_hold else self.inner_hold
        self.institutional_hold = self.institutional_hold.strip() if self.institutional_hold else self.institutional_hold
        self.total = self.total.strip() if self.total else self.total

        # 转化成float，换算单位
        self.total = float(self.total) * pow(10, 9) if self.total and '-' not in self.total else 0.0
