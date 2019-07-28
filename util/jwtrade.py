import pandas as pd

class Trade:
    # 初始现金
    cash = 100000;

    # 最大持股数量
    stock_count_max = 15;

    # 持仓明细
    hold = pd.DataFrame({'code':['1'], 'count':[1]})

    # 交易记录

    def __init__(self):
        return

    # 按目标金额下单，即将持仓市值调整至目标金额
    def order_target_value(self, code, price, target_value):

        # 计算出需要保留的股票数量
        target_count = (int((target_value / price) / 100)) * 100

        # 当前持仓的数量
        stock_hold = self.hold[self.hold['code'] == code]
        hold_count = 0
        in_hold_list = False
        if(len(stock_hold) != 0):
            hold_count = stock_hold['count'][0]
            in_hold_list = True

        if(target_count > hold_count):
            # 买入
            buy_count = target_count - hold_count
            buy_value = buy_count * price

            if(self.cash < buy_value):
                print('剩余现金不足，停止购买')
                return

            self.cash -= buy_value

            if(in_hold_list):
                stock_hold['count'][0] = target_count
            else:
                target_df = pd.DataFrame({'code':[code], 'count':[target_count]})
                self.hold = self.hold.append(target_df)

            print('执行买入:', code, '买入', buy_count, '股')
            return
        elif(target_count < hold_count):
            # 卖出
            sold_count = hold_count - target_count
            sold_value = sold_count * price
            self.cash += sold_value

            if(target_count == 0):
                # 清仓
                self.hold = self.hold[~(self.hold['code'] == code)]
            else:
                stock_hold['count'] = target_count

            print('执行卖出:', code, '卖出', sold_count, '股')
            return
        else :
            print('交易目标与当前持仓相等，不进行任何交易')
            return

        return

    ### 卖单
    def sell(code, sell_price, cash):



        return


    def buy(code, cash):
        return

if __name__ == '__main__':

    t = Trade()

    # 买入
    t.order_target_value('000001.SZ', 10, 1000)

    # 买入
    t.order_target_value('000002.SZ', 23, 50000)

    # 买入
    t.order_target_value('000001.SZ', 13, 20000)

    print(t.hold)

    print(t.cash)
