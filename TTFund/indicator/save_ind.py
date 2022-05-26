import pandas as pd
from feapder.db.mysqldb import MysqlDB
from feapder.utils.log import log

from indicators import NetProcess, Indicators
from pool import ThreadPool


# 建立 redis 连接
db = MysqlDB(
    ip="127.0.0.1", port=3306, db="ttfund", user_name="root", user_pass="717216"
)


def get_fund_net(code):
    """获取基金代码对应的净值"""

    sql = f'select id, code, date, net_worth from fund_net where code={code}'
    data = db.find(sql, to_json=True)

    df = pd.DataFrame(data)
    df.columns = ['id', '基金代码', '日期', '累计净值']

    return df


def cal_main_indicator(df):
    """计算主要指标"""

    _id = df['id']
    del df['id']

    # 计算主要指标
    ind = NetProcess(df=df)
    df = ind.run()
    df['id'] = _id

    save_main_indicator(df)

    return df


def cal_other_indicator(df):
    """计算衍生指标"""

    _id = df['id']
    del df['id']

    # 计算衍生指标
    ind = Indicators(df=df)
    data = ind.run()
    save_other_indicator(data)


def save_main_indicator(df):
    """将生成的主要指标数据更新到 mysql"""

    items = df.T.to_dict().values()
    for i in items:
        status = db.update_smart(
            table='fund_net',
            data={'range': i['涨跌幅'], 'pull_back': i['回撤幅度'], 'replace_day': i['回补天数']},
            condition=f'id={i["id"]}'
        )
        log.debug(f'正在更新主要指标---{i}更新状态为：{status}')


def save_other_indicator(data: dict):
    """将指标数据保存到 mysql"""

    fund_id = db.find('select id from fund_indicator where `基金代码`=%s' % data['基金代码'])
    if not fund_id:
        status = db.add_smart('fund_indicator', data)
        log.info(f'正在插入指标：{data}---插入状态为：{status}')
    else:
        code = data.pop('基金代码')
        status = db.update_smart(
            table='fund_indicator',
            data=data,
            condition=f'`基金代码`={code}'
        )
        log.info(f'{code}基金代码已存在，正在更新指标---更新状态为：{status}')


def main(code):

    log.info(f'{code}基金即将开始处理')

    df = get_fund_net(code)
    df = cal_main_indicator(df)
    cal_other_indicator(df)

    log.info(f'{code}基金处理完成')


if __name__ == '__main__':

    sql = 'select code from fund_list'
    code_list = db.find(sql, to_json=True)

    pool = ThreadPool(10)
    for i in code_list:
        code = i['code']
        pool.apply_async(main, (code, ))

    pool.join()
