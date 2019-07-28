# from backtest.research.research_api import *
# from backtest.research import *

# from scipy.stats import rankdata
# import scipy as sp
import numpy as np
import pandas as pd
import tushare as ts
import Constants as const
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

        price = ts.pro_bar(ts_code=index, adj='qfq', start_date=start_date, end_date=end_date)

        ## 设置索引
        price.set_index(['trade_date'],inplace=True)

        ## 升序排序
        self.price = price.sort_index()

        ###分别取开盘价，收盘价，最高价，最低价，最低价，均价，成交量#######
        # self.open_price = price.loc['open', :, :].dropna(axis=1, how='any')
        self.open_price = price['open']
        self.close = price['close']
        self.low = price['low']
        self.high = price['high']
        self.pct_chg = price['pct_chg']
        self.volume = price['vol']

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

    def alpha_009(self):
        temp = (self.high + self.low) * 0.5 - (self.high.shift() + self.low.shift()) * 0.5 * (
                    self.high - self.low) / self.volume  # 计算close_{i-1}
        # result = pd.ewma(temp, alpha=2 / 7)

        result = pd.DataFrame.ewm(temp, alpha=2 / 7)

        alpha = result.iloc[-1, :]
        return alpha.dropna()

    def alpha_002(self):
        ##### -1 * delta((((close-low)-(high-close))/((high-low)),1))####
        #### ((收盘价-最低价) - (最高价-收盘价))/(最高价-最低价)前一天差值

        result = ((self.close - self.low) - (self.high - self.close)) / ((self.high - self.low)).diff()
        m = result.iloc[1:].dropna()
        alpha = m[(m < np.inf) & (m > -np.inf)]  # 去除值为inf
        return alpha.dropna()

    ##################################################################
    def alpha_011(self):
        temp = ((self.close - self.low) - (self.high - self.close)) / (self.high - self.low)
        result = temp * self.volume
        alpha = result.iloc[-6:].sum()
        return alpha.dropna()

    #
    # def alpha_005(self):
    #     ts_volume = (self.volume.iloc[-7:]).rank(axis=0, pct=True)
    #     ts_high = (self.high.iloc[-7:]).rank(axis=0, pct=True)
    #     corr_ts = ts_high.rolling(5).corr(ts_volume)
    #     # corr_ts = pd.rolling_corr(ts_high, ts_volume, 5)
    #     alpha = corr_ts.max().dropna()
    #     alpha = alpha[(alpha < np.inf) & (alpha > -np.inf)]  # 去除inf number
    #     return alpha

    # def alpha_004(self):
    #     print(self.close.rolling(8).std())
    #     # condition1 = (pd.rolling_std(self.close, 8) < pd.rolling_sum(self.close, 2) / 2)
    #     condition1 = (self.close.rolling(8).std() < self.close.rolling(2).sum() / 2)
    #     # condition2 = (pd.rolling_sum(self.close, 2) / 2 < (
    #     #             pd.rolling_sum(self.close, 8) / 8 - pd.rolling_std(self.close, 8)))
    #     condition2 = (self.close.rolling(2).sum() / 2 < (
    #                 self.close.rolling(8).sum() / 8 - self.close.rolling(8).std()))
    #     # condition3 = (1 <= self.volume / pd.rolling_mean(self.volume, 20))
    #     condition3 = (1 <= self.volume / self.volume.rolling(20).mean())
    #     condition3
    #
    #     # indicator1 = pd.DataFrame(np.ones(self.close.shape), index=self.close.index,
    #     #                           columns=self.close.columns)  # [condition2]
    #     indicator1 = pd.DataFrame(np.ones(self.close.shape), index=self.close.index,
    #                               columns=[self.ts_code])  # [condition2]
    #
    #     indicator2 = -pd.DataFrame(np.ones(self.close.shape), index=self.close.index,
    #                                columns=[self.ts_code])  # [condition3]
    #
    #     # part0 = pd.rolling_sum(self.close, 8) / 8
    #     part0 = self.close.rolling(8).sum() / 8
    #
    #     part1 = indicator2[condition1].fillna(0)
    #     part2 = (indicator1[~condition1][condition2]).fillna(0)
    #     part3 = (indicator1[~condition1][~condition2][condition3]).fillna(0)
    #     part4 = (indicator2[~condition1][~condition2][~condition3]).fillna(0)
    #
    #     result = part0 + part1 + part2 + part3 + part4
    #     alpha = result.iloc[-1, :]
    #     return alpha.dropna()

if __name__ == '__main__':
    f = gtja_191(start_date='20190610', end_date='20190625', index='000001.SZ')

    # sorted_alpha = f.alpha_002().sort_values(ascending=True, na_position='last')

    print(f.alpha_002())

    print(f.alpha_011())

    # print(f.alpha_002())

    # f.alpha_002().plot()

    # plt.show()
