# from backtest.research.research_api import *
# from backtest.research import *

# from scipy.stats import rankdata
# import scipy as sp
import numpy as np
import pandas as pd
import tushare as ts
import Constants as const
from sklearn import datasets,linear_model
import matplotlib.pyplot as plt

ts.set_token(const.TUSHARE_TOKEN)
pro = ts.pro_api()

'''
http://quant.10jqka.com.cn/platform/html/article.html#id/87141839/q/mindgo_59547441_733
'''

class gtja_191:

    def __init__(self, start_date, end_date, index):
        # security = get_index_stocks(index)

        # price = get_price(security, None, end_date, '1d',
        #                   ['open', 'close', 'low', 'high', 'avg_price', 'prev_close', 'volume', 'turnover'], False,
        #                   None, 250, is_panel=1)
        # benchmark_price = get_price(index, None, end_date, '1d',
        #                             ['open', 'close', 'low', 'high', 'avg_price', 'prev_close', 'volume'], False, None,
        #                             250, is_panel=1)

        self.price = ts.pro_bar(ts_code=index, adj='qfq', start_date=start_date, end_date=end_date)

        ## 设置索引
        self.price.set_index(['trade_date'],inplace=True)

        ## 升序排序
        self.price = self.price.sort_index()

        ###分别取开盘价，收盘价，最高价，最低价，最低价，均价，成交量#######
        # self.open_price = price.loc['open', :, :].dropna(axis=1, how='any')
        self.open_price = self.price['open']
        self.close = self.price['close']
        self.low = self.price['low']
        self.high = self.price['high']
        self.pct_chg = self.price['pct_chg']
        self.volume = self.price['vol']

        self.ts_code = index

        # self.close = price.loc['close', :, :].dropna(axis=1, how='any')
        # self.low = price.loc['low', :, :].dropna(axis=1, how='any')
        # self.high = price.loc['high', :, :].dropna(axis=1, how='any')
        # self.avg_price = price.loc['avg_price', :, :].dropna(axis=1, how='any')
        # self.prev_close = price.loc['prev_close', :, :].dropna(axis=1, how='any')
        # self.volume = price.loc['volume', :, :].dropna(axis=1, how='any')
        # self.amount = price.loc['turnover', :, :].dropna(axis=1, how='any')
        # self.benchmark_open_price = benchmark_price.loc[:, 'open']
        # self.benchmark_close_price = benchmark_price.loc[:, 'close']
        #########################################################################

    def get_price(self):
        return self.price

    def alpha_002(self):
        ##### -1 * delta((((close-low)-(high-close))/((high-low)),1))####
        #### ((收盘价-最低价) - (最高价-收盘价))/(最高价-最低价)前一天差值

        result = ((self.close - self.low) - (self.high - self.close)) / ((self.high - self.low)).diff()
        m = result.iloc[1:].dropna()
        alpha = m[(m < np.inf) & (m > -np.inf)]  # 去除值为inf
        return alpha.dropna()

    ##################################################################
    def alpha_031(self):
        # result = (self.close - pd.rolling_mean(self.close, 12)) * 100 / pd.rolling_mean(self.close, 12)
        alpha = (self.close - self.close.rolling(12).mean()) * 100 / self.close.rolling(12).mean()

        # alpha = result.iloc[-1, :]
        return alpha.dropna()


if __name__ == '__main__':
    f = gtja_191(start_date='20190510', end_date='20190625', index='000001.SZ')

    # sorted_alpha = f.alpha_002().sort_values(ascending=True, na_position='last')


    ap_002 =  f.alpha_002()

    ap_002_df = pd.DataFrame(ap_002.values, columns=['alpha_002'], index=ap_002.index)

    print(ap_002_df)


    ap_031 =  (f.alpha_031())

    ap_031_df = pd.DataFrame(ap_031.values, columns=['alpha_031'], index=ap_031.index)

    print(ap_031_df)

    ret = pd.merge(ap_002_df, ap_031_df, on=['trade_date'])

    dt = (pd.merge(f.get_price()['pct_chg'], ret, on=['trade_date'])).values


    X = dt[:,1:]
    Y = dt[0,:]

    # # 建立模型
    regr = linear_model.LinearRegression()

    # # # 训练数据
    regr.fit(X,Y)

    # # # 拿到相关系数
    print('coefficients(b1,b2...):',regr.coef_)
    print('intercept(b0):',regr.intercept_)
