# -- coding:utf-8 --

import warnings

import pymysql
import tushare as ts
from pylab import *
from matplotlib.font_manager import FontProperties
font_set = FontProperties(fname=r"D:\PycharmProjects\JXQuant\simfang.ttf", size=12)

import Cap_Update_daily as cap_update
import Constants as const
import Filter
import Model_Evaluate as ev
import Portfolio as pf
import logging

warnings.filterwarnings("ignore")


def get_sharp_rate():
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()

    sql_cap = "select * from my_capital a order by seq asc"
    cursor.execute(sql_cap)
    done_exp = cursor.fetchall()
    db.commit()
    cap_list = [float(x[0]) for x in done_exp]
    return_list = []
    base_cap = float(done_exp[0][0])
    for i in range(len(cap_list)):
        if i == 0:
            return_list.append(float(1.00))
        else:
            ri = (float(done_exp[i][0]) - float(done_exp[0][0])) / float(done_exp[0][0])
            return_list.append(ri)
    std = float(np.array(return_list).std())
    exp_portfolio = (float(done_exp[-1][0]) - float(done_exp[0][0])) / float(done_exp[0][0])
    exp_norisk = 0.04 * (5.0 / 12.0)
    sharp_rate = (exp_portfolio - exp_norisk) / (std)

    return sharp_rate, std


if __name__ == '__main__':

    # 建立数据库连接,设置tushare的token,定义一些初始化参数
    db = pymysql.connect(host='127.0.0.1', user='root', passwd='admin', db='stock', charset='utf8')
    cursor = db.cursor()
    ts.set_token(const.TUSHARE_TOKEN)
    pro = ts.pro_api()
    year = 2018
    date_seq_start = str(year) + '-03-01'
    date_seq_end = str(year) + '-03-10'
    stock_pool = ['603912.SH', '300666.SZ', '300618.SZ', '002049.SZ', '300672.SZ']

    # 先清空之前的测试记录,并创建中间表
    sql_wash1 = 'delete from my_capital where seq != 1'
    cursor.execute(sql_wash1)
    db.commit()
    sql_wash3 = 'truncate table my_stock_pool'
    cursor.execute(sql_wash3)
    db.commit()
    # 清空行情源表，并插入相关股票的行情数据。该操作是为了提高回测计算速度而剔除行情表(stock_all)中的冗余数据。
    sql_wash4 = 'truncate table stock_info'
    cursor.execute(sql_wash4)
    db.commit()
    # 清空model_ev_resu
    sql_wash5 = 'truncate table model_ev_resu'
    cursor.execute(sql_wash5)
    db.commit()

    in_str = '('
    for x in range(len(stock_pool)):
        if x != len(stock_pool) - 1:
            in_str += str('\'') + str(stock_pool[x]) + str('\',')
        else:
            in_str += str('\'') + str(stock_pool[x]) + str('\')')
    sql_insert = "insert into stock_info(select * from stock_all a where a.stock_code in %s)" % (in_str)
    cursor.execute(sql_insert)
    db.commit()

    # 建回测时间序列
    back_test_date_start = (datetime.datetime.strptime(date_seq_start, '%Y-%m-%d')).strftime('%Y%m%d')
    back_test_date_end = (datetime.datetime.strptime(date_seq_end, "%Y-%m-%d")).strftime('%Y%m%d')
    # 获取回测时间内的交易日
    # trade_cal的文档：https://tushare.pro/document/2?doc_id=26
    df = pro.trade_cal(exchange_id='', is_open=1, start_date=back_test_date_start, end_date=back_test_date_end)

    # dataframe 的文档：https://www.cnblogs.com/IvyWong/p/9203981.html
    date_temp = list(df.iloc[:, 1])
    date_seq = [(datetime.datetime.strptime(x, "%Y%m%d")).strftime('%Y-%m-%d') for x in date_temp]
    print(date_seq)

    # 开始模拟交易
    index = 1
    day_index = 0
    for i in range(1, len(date_seq)):
        day_index += 1
        # 每日推进式建模，并获取对下一个交易日的预测结果
        for stock in stock_pool:
            try:
                ans2 = ev.model_eva(stock, date_seq[i], 90, 365)
                print('Date : ' + str(date_seq[i]) + ' Update : ' + str(stock))
            except Exception as ex:
                print(ex)
                logging.exception(ex)
                continue
        # 每5个交易日更新一次配仓比例
        if divmod(day_index + 4, 5)[1] == 0:
            portfolio_pool = stock_pool
            if len(portfolio_pool) < 5:
                print('Less than 5 stocks for portfolio!! state_dt : ' + str(date_seq[i]))
                continue
            pf_src = pf.get_portfolio(portfolio_pool, date_seq[i - 1], year)
            # 取最佳收益方向的资产组合
            risk = pf_src[1][0]
            weight = pf_src[1][1]
            Filter.filter_main(portfolio_pool, date_seq[i], date_seq[i - 1], weight)
        else:
            Filter.filter_main([], date_seq[i], date_seq[i - 1], [])
            cap_update_ans = cap_update.cap_update_daily(date_seq[i])
        print('Runnig to Date :  ' + str(date_seq[i]))
    print('ALL FINISHED!!')

    sharp, c_std = get_sharp_rate()
    print('Sharp Rate : ' + str(sharp))
    print('Risk Factor : ' + str(c_std))

    # 取上证指数每日行情数据
    sql_show_btc = "select * from stock_index a where a.stock_code = 'SH' and a.state_dt >= '%s' and a.state_dt <= '%s' order by state_dt asc" % (
        date_seq_start, date_seq_end)
    cursor.execute(sql_show_btc)
    done_set_show_btc = cursor.fetchall()
    # btc_x = [x[0] for x in done_set_show_btc]
    btc_x = list(range(len(done_set_show_btc)))

    # done_set_show_btc[0][3] 是指以回测的第一天的收盘价作为基准线，后续每一天的收盘价/第一天收盘价作为计算大盘收益率曲线
    # 计算大盘收益率曲线
    btc_y = [x[3] / done_set_show_btc[0][3] for x in done_set_show_btc]
    dict_anti_x = {}
    dict_x = {}
    for a in range(len(btc_x)):
        dict_anti_x[btc_x[a]] = done_set_show_btc[a][0]
        dict_x[done_set_show_btc[a][0]] = btc_x[a]

    # sql_show_profit = "select * from my_capital order by state_dt asc"
    # 计算持仓收益率
    sql_show_profit = "select max(a.capital),a.state_dt from my_capital a where a.state_dt is not null group by a.state_dt order by a.state_dt asc"
    cursor.execute(sql_show_profit)
    done_set_show_profit = cursor.fetchall()
    profit_x = [dict_x[x[1]] for x in done_set_show_profit]
    # 以回测第一天的持仓资金总量作为基准线，后续每一天的持仓资金总量/第一天的资金总量来计算持仓收益率曲线
    profit_y = [x[0] / done_set_show_profit[0][0] for x in done_set_show_profit]


    # 绘制收益率曲线（含大盘基准收益曲线）
    def c_fnx(val, poz):
        if val in dict_anti_x.keys():
            return dict_anti_x[val]
        else:
            return ''


    fig = plt.figure(figsize=(10, 4))
    plt.title(u'收益率曲线', fontproperties=font_set)
    # 111”表示“1×1网格，第一子图
    ax = fig.add_subplot(111)
    # x轴转换
    ax.xaxis.set_major_formatter(FuncFormatter(c_fnx))
    # 上证收益率曲线
    plt.plot(btc_x, btc_y, color='blue')
    # 策略收益率曲线
    plt.plot(profit_x, profit_y, color='red')
    # 显示图例
    plt.legend(["000001 Profit Rate","My Strategy"])

    plt.show()

    cursor.close()
    db.close()
