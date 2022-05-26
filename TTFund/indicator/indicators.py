from datetime import datetime

import pandas as pd


class NetProcess:
    """ 计算主要指标 API """

    def __init__(self, df: pd.DataFrame):

        self.df = df
        self.name = self.df['基金代码'][0]

    def run(self):

        self.xrange()
        self.withdrawal()
        self.replace_days()

        return self.df

    def xrange(self):
        """计算涨跌幅"""

        self.df['涨跌幅'] = self.df['累计净值'] / self.df['累计净值'].shift(1) - 1
        self.df.loc[0, '涨跌幅'] = self.df['累计净值'][0] - 1
        self.df['涨跌幅'] = self.df['涨跌幅'] * 100

    def withdrawal(self):
        """计算实时回撤"""

        self.df['回撤幅度'] = 0
        for i in self.df.itertuples():
            tmp_df = self.df.iloc[:i.Index]

            if tmp_df.empty:
                continue

            if tmp_df['累计净值'].max() >= i[3]:
                self.df.loc[i.Index, '回撤幅度'] = i[3] / tmp_df['累计净值'].max() - 1

        self.df['回撤幅度'] = self.df['回撤幅度'] * 100

    def replace_days(self):
        """计算回补天数"""

        for i in self.df.iterrows():
            index, series = i

            tmp_df = self.df.loc[:index, '累计净值']
            max_index = int(tmp_df[tmp_df == tmp_df.max()].index[-1])

            if series['累计净值'] <= tmp_df.max():
                day = int(index - max_index)
                self.df.loc[index, '回补天数'] = day
            else:
                self.df.loc[index, '回补天数'] = 0

        self.df['回补天数'] = self.df['回补天数'].astype(int)


class Indicators:
    """ 计算衍生指标 API """

    def __init__(self, df: pd.DataFrame):

        self.df = df
        self.name = self.df['基金代码'][0]
        self.df['日期'] = pd.to_datetime(self.df['日期'])

    def run(self):

        self.establish_time()
        self.operate_days()
        self.cum_return_rate()
        self.annualized_rate()
        self.year_rate()
        self.max_withdrawal()
        self.max_replace_day()
        self.return_wit_rate()

        self.sharpe()

        self.win_rate()
        self.pl_ratio()
        self.avg_increase()
        self.avg_decline()
        self.avg_pl_ratio()
        self.max_increase()
        self.max_decline()
        self.new_date()
        self.new_value()
        self.new_wit()
        self.wit_pre()

        data = self.df.round(5).iloc[-1].to_dict()
        data.pop('日期')
        data.pop('累计净值')
        data.pop('涨跌幅')
        data.pop('回撤幅度')
        data.pop('回补天数')
        data['成立时间'] = str(data['成立时间'].date())
        data['最新日期'] = str(data['最新日期'].date())

        return data

    def establish_time(self):
        """计算成立时间"""

        self.df['成立时间'] = self.df['日期'][0]

    def operate_days(self):
        """计算运作天数"""

        # 包含非交易日
        start_day = self.df.iloc[0]['日期']
        end_day = self.df.iloc[-1]['日期']

        self.df['运作天数'] = (end_day - start_day).days

    def cum_return_rate(self):
        """计算累计收益率"""

        self.df['累计收益率'] = (self.df['累计净值'].iloc[-1] - 1) * 100

    def annualized_rate(self):
        """计算年化收益率"""

        year = self.df['运作天数'] / 365
        self.df['年化收益率'] = self.df['累计收益率'] / year

    def year_rate(self):
        """计算今年收益率"""

        year = datetime.now().year
        tmp_df = self.df[self.df['日期'] > datetime(year, 1, 1)]

        self.df['今年收益率'] = (self.df['累计净值'].iloc[-1] - tmp_df['累计净值'].iloc[0]) * 100

    def max_withdrawal(self):
        """计算最大回撤"""

        self.df['最大回撤'] = self.df['回撤幅度'].abs().max()

    def max_replace_day(self):
        """最大回补天数"""

        self.df['最大回补天数'] = self.df['回补天数'].max()

    def return_wit_rate(self):
        """计算年化收益与最大回撤比"""

        if self.df['最大回撤'].any():
            self.df['年化收益与最大回撤比'] = self.df['年化收益率'] / self.df['最大回撤']
        else:
            self.df['年化收益与最大回撤比'] = 0

    def sharpe(self):
        """计算夏普比"""
        # 夏普比率 = （投资组合预期收益率 - 无风险利率）/ 投资组合的波动率
        # 夏普比率 = （年化收益率 - 十年期国债收益率）/ 净值标准差

        # 十年期国债收益率 %
        debt_rate_10 = 3.48
        if self.df['累计净值'].std():
            self.df['夏普比'] = (self.df['年化收益率'] - debt_rate_10) / self.df['累计净值'].std()
        else:
            self.df['夏普比'] = 0

    def win_rate(self):
        """计算胜率"""

        self.df['胜率'] = len(self.df['涨跌幅'][self.df['涨跌幅'] > 0]) / len(self.df)

    def pl_ratio(self):
        """计算盈亏次数比"""

        win_count = len(self.df['涨跌幅'][self.df['涨跌幅'] > 0])
        loss_count = len(self.df['涨跌幅'][self.df['涨跌幅'] < 0])

        self.df['盈亏次数比'] = f'{win_count}/{loss_count}'

    def avg_increase(self):
        """计算单日平均涨幅"""

        tmp_df = self.df['涨跌幅'][self.df['涨跌幅'] > 0]
        if tmp_df.empty:
            self.df['单日平均涨幅'] = 0
        else:
            self.df['单日平均涨幅'] = tmp_df.sum() / len(tmp_df)

    def avg_decline(self):
        """计算单日平均跌幅"""

        tmp_df = self.df['涨跌幅'][self.df['涨跌幅'] < 0]
        if tmp_df.empty:
            self.df['单日平均跌幅'] = 0
        else:
            self.df['单日平均跌幅'] = tmp_df.sum() / len(tmp_df)

    def avg_pl_ratio(self):
        """计算平均盈亏比"""

        if self.df['单日平均跌幅'].abs().any():
            self.df['平均盈亏比'] = self.df['单日平均涨幅'] / self.df['单日平均跌幅'].abs()
        else:
            self.df['平均盈亏比'] = 0

    def max_increase(self):
        """计算单日最大涨幅"""

        self.df['单日最大涨幅'] = self.df['涨跌幅'].max()

    def max_decline(self):
        """计算单日最大跌幅"""

        self.df['单日最大跌幅'] = self.df['涨跌幅'].min()

    def new_date(self):
        """计算最新日期"""

        self.df['最新日期'] = self.df['日期'].iloc[-1]

    def new_value(self):
        """计算最新净值"""

        self.df['最新净值'] = self.df['累计净值'].iloc[-1]

    def new_wit(self):
        """计算最新回撤幅度"""

        self.df['最新回撤幅度'] = self.df['回撤幅度'].iloc[-1]

    def wit_pre(self):
        """计算最新回撤分位数"""

        if self.df['回撤幅度'].abs().any():
            self.df['最新回撤分位数'] = self.df['最新回撤幅度'].abs()[0] / (
                    self.df['回撤幅度'].abs().max() - self.df['回撤幅度'].abs().min()
            )
        else:
            self.df['最新回撤分位数'] = 0

    def adjust_frequent(self):
        """计算调仓频率"""
        ...
