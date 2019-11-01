import pandas as pd
import util.jwdata as jd
from pylab import *

### 1. 没有止损&止盈
### 2. 没有交易成本
### 3. 交易明细待补充
### 鲁棒性待测试：停复牌的情况
class Trade:

    # 回测开始时间
    backtest_start_date = None
    # 回测结束时间
    backtest_end_date = None
    # 当前时间
    current_day = None
    # 尽力购买（当现金不足以购买指定数量时，使用剩余现金能买多少买多少）
    try_all = False

    # 初始现金
    init_cash = 100000

    # 当前现金
    cash = init_cash

    # 最大持股数量
    stock_hold_max = 15

    # 持仓明细git
    hold = pd.DataFrame({'code':['1'], 'count':[1], 'avg_buy_price':[1]})
    hold = hold.drop([0])
    # 交易记录
    # 日期 证券资产 现金余额 总资产
    # 当前持仓明细（股票代码 买入均价 今日收盘价 持仓数量 资产总值）
    # daily_hold_detail =

    daily_capital = None

    # 构建函数
    def __init__(self, try_all=False, backtest_start_date = '20120101', backtest_end_date = '20190801'):
        self.backtest_start_date = backtest_start_date
        self.backtest_end_date = backtest_end_date
        self.try_all = try_all
        return

    # 每日运行
    def run_daily(self, callback):

        # 获取交易日
        trade_days = jd.get_cal(self.backtest_start_date, self.backtest_end_date)

        # 执行每日的交易回调
        pre_day = None
        for day in trade_days:
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

            self.current_day = day
            callback(self)

            self.hold.set_index('code', drop=False, inplace=True)

            # 空仓
            if len(self.hold) == 0:
                today_capital = pd.DataFrame(
                    {'date': [day], 'stock_value': [0], 'total_value': [self.cash]})

                if self.daily_capital is None:
                    self.daily_capital = today_capital
                else:
                    self.daily_capital = self.daily_capital.append(today_capital)
                continue

            # 清算每日持仓
            # 获取当天收盘价
            pn = jd.get_price_panel(list(self.hold['code']), day, day)
            curr_close = pn['close', day, :]
            # 处理停牌的情况
            suspend_stock_list = curr_close[isnan(curr_close)].index.tolist()
            if(len(suspend_stock_list) == 0):
                self.hold['curr_close'] = curr_close
            else:
                print('持仓中有股票停牌', suspend_stock_list)
                suspend_hold = self.hold[np.isin(self.hold['code'], np.array(suspend_stock_list))]
                self.hold['curr_close'] = curr_close[~isnan(curr_close)].append(suspend_hold['curr_close'])

            # 当日股票市值
            curr_stock_value = (self.hold['curr_close'] * self.hold['count']).sum()
            curr_total_value = curr_stock_value + self.cash

            today_capital = pd.DataFrame(
                {'date': [day], 'stock_value': [curr_stock_value], 'total_value': [curr_total_value]})
            if(self.daily_capital is None):
                self.daily_capital = today_capital
            else:
                self.daily_capital = self.daily_capital.append(today_capital)


            print('今日（', day, '）持仓明细：\r\n', self.hold)
            print('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\r\n')

            pre_day = day
        return

    # 按目标金额下单，即将持仓市值调整至目标金额
    def order_target_value(self, code, price, target_value):

        # 计算出需要保留的股票数量
        target_count = (int((target_value / price) / 100)) * 100

        # 当前持仓的数量
        stock_hold = self.hold[self.hold['code'] == code]
        hold_count = 0
        in_hold_list = False
        if len(stock_hold) != 0:
            hold_count = stock_hold['count'][0]
            in_hold_list = True

        if target_count > hold_count:
            if len(stock_hold) >= self.stock_hold_max:
                print('超过股票最大持仓个数，停止购买')

            # 买入
            buy_count = target_count - hold_count
            buy_value = buy_count * price

            # 剩余现金不足
            if self.cash < buy_value:
                if self.try_all is False:
                    print('剩余现金不足，停止购买')
                    return

                # 尽力购买
                buy_count = (int((self.cash / price) / 100)) * 100
                if buy_count <= 0:
                    print('剩余现金不足，尝试购买失败')
                    return

                print('剩余现金不足，尽力购买')
                buy_value = buy_count * price

            self.cash -= buy_value

            real_target_count = hold_count + buy_count
            # 加仓
            if in_hold_list:
                # 计算平均买入成本
                self.hold.loc[self.hold['code'] == code, 'avg_buy_price'] = (buy_value + stock_hold['avg_buy_price'][0] * hold_count) / real_target_count
                self.hold.loc[self.hold['code'] == code, 'count'] = real_target_count
            else:
                # 首次持仓
                target_df = pd.DataFrame({'code':[code], 'count':[real_target_count], 'avg_buy_price':[price]})
                self.hold = self.hold.append(target_df)

            print('执行买入:', code, '加仓' if in_hold_list else '买入', buy_count, '股', '价格:', price, '；剩余现金:', self.cash)
        elif target_count < hold_count:
            # 卖出
            sold_count = hold_count - target_count
            sold_value = sold_count * price
            self.cash += sold_value

            if target_count == 0:
                # 清仓
                self.hold = self.hold[~(self.hold['code'] == code)]
            else:
                self.hold.loc[self.hold['code'] == code, 'count'] = target_count

            print('执行卖出:', code, '卖出', sold_count, '股', '价格:', price, '剩余现金:', self.cash)
        else :
            if target_value >= 0:
                print('交易目标与当前持仓相等，不进行任何交易')
            return

        # print('当前持仓明细：')
        # print(self.hold)
        # print('==========================================')

        return

    def show(self):
        # 设置索引
        self.daily_capital.set_index('date', inplace=True, drop=False)

        # 净值曲线量纲缩放
        # basic_value = self.daily_capital['total_value'][0]
        basic_value = self.init_cash
        (self.daily_capital['total_value'] / basic_value).plot(label="strategy1", style='b-o')

        # pfyh = jd.get_price_panel(['600000.SH'], self.backtest_start_date, self.backtest_end_date)
        # pfyh = pfyh['close', :, :]['600000.SH']
        # (pfyh / pfyh[0]).plot(label="600000.SH", style='r-*')

        hs300 = jd.getHS300(self.backtest_start_date, self.backtest_end_date)
        hs300_basic = hs300['close'][0]
        (hs300['close'] / hs300_basic).plot(label="hs300", style='r-*')

        # 展示
        plt.grid(axis="both", linestyle='--')
        plt.legend()
        plt.show()
        return
