import tushare as ts
import pandas as pd
import datetime

import warnings
warnings.filterwarnings("ignore")

ts.set_token('d3fdbde82434cd6d7897550852136449f9fcba912e3eacb47b004600')
pro = ts.pro_api()

# 获取交易日
def get_cal(date_seq_start, date_seq_end):

    # 获取交易日
    df = pro.trade_cal(exchange_id='', is_open=1, start_date=date_seq_start, end_date=date_seq_end)
    date_seq = list(df.iloc[:, 1])
    # date_seq = [(datetime.datetime.strptime(x, "%Y%m%d")).strftime('%Y-%m-%d') for x in date_temp]
    return date_seq

# 获取价格
def get_price_panel(codes, start, end):
    open_data = {}
    close_data = {}
    low_data = {}
    high_data = {}
    prev_close_data = {}
    # 成交量
    volume_data = {}
    # 成交额
    turnover_data = {}

    for code in codes:
        df = ts.pro_bar(ts_code=code, adj='qfq', start_date=start, end_date=end)
        # df = ts.pro_bar(ts_code=code, start_date=start, end_date=end)
        # 设置索引
        df.set_index('trade_date', inplace=True)
        # 按照日期顺序排序
        price = df.sort_values(by='trade_date', ascending=True)

        open_data[code] = price['open']
        close_data[code] = price['close']
        low_data[code] = price['low']
        high_data[code] = price['high']
        prev_close_data[code] = price['pre_close']
        volume_data[code] = price['vol']
        turnover_data[code] = price['amount']

    open_df = pd.DataFrame(open_data)
    close_df = pd.DataFrame(close_data)
    low_df = pd.DataFrame(low_data)
    high_df = pd.DataFrame(high_data)
    prev_close_df = pd.DataFrame(prev_close_data)
    volume_df = pd.DataFrame(volume_data)
    turnover_df = pd.DataFrame(turnover_data)

    # 创建panel
    panel_data = {'open': open_df, 'close': close_df, 'low': low_df, 'high':high_df, 'prev_close':prev_close_df, 'volume':volume_df, 'turnover':turnover_df}
    pl = pd.Panel(panel_data)

    return pl

def getHS300(start=None, end=None):
    start = (datetime.datetime.strptime(start, "%Y%m%d")).strftime('%Y-%m-%d')
    end = (datetime.datetime.strptime(end, "%Y%m%d")).strftime('%Y-%m-%d')
    df = ts.get_hist_data(code='hs300', start=start, end=end)

    df.sort_index(inplace=True, ascending=True)

    return df

if __name__ == '__main__':




    start = '20190715'
    end = '20190726'

    d = getHS300(start, end) # 获取沪深300指数k线数据

    # pl = get_price_panel(['000001.SZ', '000002.SZ', '000020.SZ', '000505.SZ'], start, end)


    pl = get_price_panel(['000505.SZ'], start, end)

    print('open')
    print(pl['open', :, :])

    print('close')
    print(pl['close', :, :])

    print('low')
    print(pl['low', :, :])


    print('high')
    print(pl['high', :, :])


    print('volume')
    print(pl['volume', :, :])

    print('prev_close')
    print(pl['prev_close', :, :])


    print('turnover')
    print(pl.loc['turnover',:,:].dropna(axis=1,how='any'))