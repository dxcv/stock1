import pandas as pd
from sqlalchemy import create_engine
import  datetime

# 初始化数据库连接，使用pymysql模块
engine = create_engine('mysql+pymysql://root:admin@localhost:3306/my_stock')

def get_price(code=None, start_date=None, end_date=None, ascending=True):

    start = datetime.datetime.strptime(start_date, "%Y%m%d").strftime('%Y-%m-%d')
    end = datetime.datetime.strptime(end_date, "%Y%m%d").strftime('%Y-%m-%d')

    # 查询语句，选出employee表中的所有数据
    sql =  '''
        SELECT
            code, date as trade_date, open, high, low, close, vol, amount, pre_close from stock_daily
        WHERE `code` = '%s' AND date >= '%s' AND date<= '%s' ORDER BY date %s
          '''%(code, start, end, 'ASC' if ascending else 'DESC')


    # read_sql_query的两个参数: sql语句， 数据库连接
    df = pd.read_sql_query(sql, engine)

    df['trade_date'] = [(datetime.datetime.strptime(x, "%Y-%m-%d")).strftime('%Y%m%d') for x in df['trade_date'].values]

    df.set_index('trade_date', inplace=True)

    return df