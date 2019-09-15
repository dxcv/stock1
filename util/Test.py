import util.JWDataFromTushare as jdt
import util.JWDataFromDB as jdd
import pandas as pd
import datetime

import tushare as ts

ts.set_token('d3fdbde82434cd6d7897550852136449f9fcba912e3eacb47b004600')
pro = ts.pro_api()


stock_list = jdd.get_stock_list()


for stock in stock_list['ts_code']:
    df = ts.pro_bar(ts_code=stock, adj='qfq', start_date='2001-01-01', end_date='2019-09-15')

    df['code'] = df['ts_code']
    df['date'] = [(datetime.datetime.strptime(x, '%Y%m%d')).strftime("%Y-%m-%d") for x in df['trade_date'].values]

    import_df = df[['code', 'date', 'open', 'high', 'low', 'close', 'vol', 'amount', 'pre_close']]

    df.to_sql('stock_daily', engine, if_exists='append', index=False)

    print("%s import done！" % (code))

# code = '000063.SZ'
code = '600000.SH'
start = '20190601'
end = '20190630'

df1 = jdt.get_price(code, start, end)
df2 = jdd.get_price(code, start, end)


for item in ['close', 'open', 'high', 'low', 'pre_close']:
    print("\r\n diff %s:"%item)
    diff_df = pd.DataFrame({'c1':df1[item], 'c2':df2[item]})
    print(diff_df[diff_df['c1'] != diff_df['c2']])