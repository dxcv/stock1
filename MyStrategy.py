import tushare as ts
import Constants as const
import datetime
import pymysql
from pylab import *

# 自己的第一个简单策略

# 1. 选股，以海康威视为例（不涉及投资组合）

# 2. 择时
# 策略核心：
# 买入时机：假设hk在连续三个交易日都下跌的时候，则在下个交易日以收盘价买入，
# 卖出时机：持有N天后以第N天的收盘价作为卖出价
# 不设置止损

# 3. 仓位管理

# 收益评估

# 目标：计算出该策略的收益率曲线，并与上证指数收益率曲线对比

# 方案：
# 第一步：先把hk的日行情数据清洗出来
# 第二步：计算每日的上三个交易日的下跌次数（因子）
# 第三步：回测

ts.set_token(const.TUSHARE_TOKEN)
pro = ts.pro_api()

db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
cursor = db.cursor()

def get_cal(date_seq_start, date_seq_end):
    back_test_date_start = (datetime.datetime.strptime(date_seq_start, '%Y-%m-%d')).strftime('%Y%m%d')
    back_test_date_end = (datetime.datetime.strptime(date_seq_end, "%Y-%m-%d")).strftime('%Y%m%d')

    # 获取交易日
    df = pro.trade_cal(exchange_id='', is_open=1, start_date=back_test_date_start, end_date=back_test_date_end)
    date_temp = list(df.iloc[:, 1])
    date_seq = [(datetime.datetime.strptime(x, "%Y%m%d")).strftime('%Y-%m-%d') for x in date_temp]
    return date_seq

"""
获取当前持仓
"""
def get_current_capital():
    # 获取最新的持仓信息
    query_capital_sql = 'SELECT * FROM my_capital2 ORDER BY state_dt DESC LIMIT 1'
    cursor.execute(query_capital_sql)
    capital_result = cursor.fetchall()
    # 总资产= 股票资产 + 现金资产
    capital_amount = float(capital_result[0][0])
    # 股票资产
    lock_amount = float(capital_result[0][1])
    # 现金资产
    rest_amount = float(capital_result[0][2])
    state_dt = float(capital_result[0][2])
    return capital_amount,lock_amount,rest_amount,state_dt

"""
获取某只股票的日线
"""
def get_daily_price(stock_code, date):
    query_stock_price_sql = 'SELECT * from stock_all where stock_code = \'%s\'  and state_dt = \'%s\'' % (
        stock_code, date)
    cursor.execute(query_stock_price_sql)
    query_stock_price_result = cursor.fetchall()
    return query_stock_price_result[0][2], query_stock_price_result[0][3]

"""
更新所有的股票现值
"""
def update_daily_capital(date):
    query_stock_sql = 'select * from my_stock_pool_buy where hold_vol > 0';

    cursor.execute(query_stock_sql)
    stock_list = cursor.fetchall()

    new_lock_amount = 0
    for a in range(len(stock_list)):
        scode = stock_list[a][1]
        open, close = get_daily_price(scode, date)

        new_lock_amount += close * stock_list[a][3]

    capital_amount,lock_amount,rest_amount,state_dt = get_current_capital();
    new_capital_amount = float(new_lock_amount) + rest_amount

    if state_dt == date:
        update_capital_sql = 'update my_capital2 set capital = %s, money_lock=%s, money_rest=%s where state_dt = \'%s\'' % (
            new_capital_amount, new_lock_amount, rest_amount, date)
    else:
        update_capital_sql = 'insert into my_capital2(capital, money_lock, money_rest, state_dt) VALUES (%s,%s,%s,\'%s\')' % (
            new_capital_amount, new_lock_amount, rest_amount, date)
    cursor.execute(update_capital_sql)
    db.commit()
    return


if __name__ == '__main__':

    stock_code = '002415.SZ'

    hold_days = 2


    date_seq_start = '2019-01-01'
    date_seq_end = '2019-06-01'

    # 获取交易日历
    date_seq = get_cal(date_seq_start, date_seq_end)
    print(date_seq)

    # 模拟每日的交易
    # 从模拟的第4个交易日开始
    for i in range(3, len(date_seq)):

        # 先卖，判断是否持仓N天以上
        sell_last_day = date_seq[i - hold_days]
        # 在这之前的股票全部卖掉，不管是涨还是跌
        query_sell_stock_sql = 'select * from my_stock_pool_buy where hold_vol > 0 and state_dt < \'%s\' and stock_code = \'%s\'' % (
        sell_last_day, stock_code)
        cursor.execute(query_sell_stock_sql)
        sell_stock_list = cursor.fetchall()

        for a in range(len(sell_stock_list)):
            hold_vol = sell_stock_list[a][3]
            # 获取今天开盘价
            query_stock_price_sql = 'SELECT * from stock_all where stock_code = \'%s\'  and state_dt in (\'%s\') ORDER BY state_dt desc' % (
                stock_code, date_seq[i])
            cursor.execute(query_stock_price_sql)
            query_stock_price_result = cursor.fetchall()

            # 当天开盘价卖出
            sell_price = query_stock_price_result[0][2]
            sell_sql = 'update my_stock_pool_buy set hold_vol=0, sell_price=%s where stock_code=\'%s\' and state_dt = \'%s\'' %(sell_price, sell_stock_list[a][1], sell_stock_list[a][0])
            cursor.execute(sell_sql)
            print("%s sell %s, vol=%s, price=%s"%(date_seq[i], sell_stock_list[a][1], str(hold_vol), str(sell_price)))

            # 更新持仓数据
            capital_amount, lock_amount, rest_amount, state_dt = get_current_capital()
            new_rest_amount = rest_amount + float(sell_price * hold_vol)
            update_capital_sql = 'insert into my_capital2(capital, money_lock, money_rest, state_dt) VALUES (%s,%s,%s,\'%s\')' % (
            capital_amount, lock_amount, new_rest_amount, date_seq[i])
            cursor.execute(update_capital_sql)
            db.commit()

        # 买入信号
        pre_index=3
        in_date_str = ''
        for j in range(i-3, i):
            if(pre_index != 3):
                in_date_str += ','
            in_date_str +=  '\'' + date_seq[j]  + '\''
            pre_index -= 1
        sql = 'SELECT * from stock_all where stock_code = \'%s\'  and state_dt in (%s) ORDER BY state_dt desc' % (stock_code, in_date_str)

        cursor.execute(sql)
        result_set = cursor.fetchall()
        db.commit()

        but_flag=True;
        for k in range(0,3):
            but_flag = but_flag and result_set[k][9] < 0
            if k == 0:
                close_price = result_set[k][3]

        if(but_flag):
            buy_price = float(close_price)

            # 获取最新的持仓信息
            capital_amount, lock_amount, rest_amount, state_dt = get_current_capital()

            # 时间，股票代码，买入价，数量(每次固定1000股)

            # 买入量这里需要控制仓位
            buy_amout = int((rest_amount * 0.8 ) /(buy_price*100)) * 100
            if buy_amout == 0:
                print("资金不足，放弃购买")
                continue

            buy_sql = 'insert into my_stock_pool_buy (state_dt, stock_code, buy_price, hold_vol) VALUES(\'%s\', \'%s\', %s, %s)' % (date_seq[i], stock_code, buy_price, buy_amout)
            cursor.execute(buy_sql)
            db.commit()
            print("%s buy %s, vol=%s, buy_price=%s"%(date_seq[i], stock_code, str(buy_amout), str(buy_price)))


            # 更新持仓数据
            # new_lock_amount = lock_amount +  buy_amout * buy_price
            new_rest_amount = rest_amount - buy_amout * buy_price

            if state_dt == date_seq[i]:
                update_capital_sql = 'update my_capital2 set capital = %s, money_lock=%s, money_rest=%s where state_dt = \'%s\'' % (
                capital_amount, lock_amount, new_rest_amount, date_seq[i])
            else:
                update_capital_sql = 'insert into my_capital2(capital, money_lock, money_rest, state_dt) VALUES (%s,%s,%s,\'%s\')' % (
                capital_amount, lock_amount, new_rest_amount, date_seq[i])

            cursor.execute(update_capital_sql)
            db.commit()

        # 每日更新股票市值
        update_daily_capital(date_seq[i])


    # 画图
    query_capital_sql = 'SELECT * FROM my_capital2 ORDER BY state_dt'
    cursor.execute(query_capital_sql)
    capital_result = cursor.fetchall()
    print(capital_result[0])
    capital_result = capital_result[1:]

    print(capital_result[0])

    x_date = [x[3] for x in capital_result]

    print(x_date)

    init_capital = float(capital_result[0][0])
    y_profit = [float(x[0]) / init_capital for x in capital_result]

    y_basic = [1 for x in capital_result]

    # 取基准数据
    basic_stock_code = '000001.SZ'
    in_date_str = ''
    for j in range(len(x_date)):
        if (j == 0):
            in_date_str += '\'' + x_date[j] + '\''
        else:
            in_date_str += ',\'' + x_date[j] + '\''

    sql = 'SELECT * from stock_all where stock_code = \'%s\'  and state_dt in (%s) ORDER BY state_dt' % (
    basic_stock_code, in_date_str)

    cursor.execute(sql)
    basic_stock_result = cursor.fetchall()

    basic_price = basic_stock_result[0][3]
    y_000001_profit = [float(x[3] / basic_price) for x in basic_stock_result]
    print(basic_stock_result[0])

    x_000001_date = [x[0] for x in basic_stock_result]

    plt.plot(x_date, y_profit, color='blue')
    plt.plot(x_000001_date, y_000001_profit, color='g')
    plt.plot(x_date, y_basic, color='red')
    plt.legend(["strategy", "000001.SZ"])

    plt.show()



