from sqlalchemy import create_engine
import tushare as ts
import Constants as const

import pymysql
pymysql.install_as_MySQLdb()

ts.set_token(const.TUSHARE_TOKEN)
pro = ts.pro_api()

# df = ts.get_tick_data('002415.SZ', date='2018-12-22')

df = pro.stock_company(exchange='SZSE', fields='ts_code')

# list_df = ts.get_sz50s()
# print(df.columns.values.tolist())
# print(df['ts_code'].values)

engine = create_engine('mysql://root:admin@127.0.0.1/my_stock?charset=utf8')

code_list = df['ts_code'].values

for code in code_list:

    df = ts.pro_bar(ts_code=code, adj='qfq', start_date="20160101", end_date="20190601")


    if df is None:
        continue

    #存入数据库
    # df.to_sql('tick_data',engine)

    #追加数据到现有表
    df.to_sql('daily_data',engine,if_exists='append')

    print("%s import done！"%(code))