import util.jwtrade as jt
import alpha.Alpha191_3 as ap
import numpy as np
import util.jwdata as jd
import data.ReadCSV as rc
import datetime

codes = jd.get_hs300_codes()
# codes = ['600111.SH', '600115.SH', '600118.SH', '600153.SH', '600170.SH']
# codes = ['000063.SZ']

pre_window = 10
compare_window = 2
down_pct = -2

def daily_callback(ctx):
    date = ctx.current_day

    print('%s 开始交易'%date)

    # 先卖空手中持仓
    if ctx.hold is not None and len(ctx.hold) >= 0:
        for hold_code in ctx.hold['code'].values:
            # 先卖空
            price = jd.get_price(hold_code, date, date)

            if len(price) <= 0:
                # 数据缺失或者停牌
                continue

            open = price['open'][0]
            ctx.order_target_value(hold_code, open, 0)

    # 择时选择
    for code in codes:

        if code.startswith('300'):
            # 过滤创业板
            continue

        f_date = (datetime.datetime.strptime(date, "%Y%m%d")).strftime('%Y-%m-%d')

        # time_df = rc.get_fast_down_time(f_date, code, pre_window, compare_window, down_pct)
        #
        # if time_df is not None and len(time_df) >= 0:
        #     for i in range(len(time_df)):
        #
        #         print('提示购买:', code, f_date,time_df.iloc[i]['datetime'], time_df.iloc[i]['c_ma'+str(compare_window)])
        #
        #         ctx.order_target_value(code, time_df.iloc[i]['c_ma'+str(compare_window)], 10000)

        time_df = rc.get_fast_down2(f_date, code, pre_window, compare_window, down_pct)

        if time_df is not None and len(time_df) >= 0:
            for i in range(len(time_df)):

                print('提示购买:', code, f_date, time_df.index[i], time_df.iloc[i]['ma'+str(compare_window)])

                ctx.order_target_value(code, time_df.iloc[i]['ma'+str(compare_window)], 10000)

    return

if __name__ == '__main__':

    t = jt.Trade(backtest_start_date='20190601', backtest_end_date='20190721', try_all=True)

    t.run_daily(daily_callback)

    print(t.daily_capital)

    t.show()



'''
0. 核心策略：捕捉形态如下
000783 2019-06-10 0954 这种急跌

1. 创业板过滤 DONE
2. 股票排序问题可能导致的运气成分
    调高阈值？
3. 数据缺失问题
4. 急涨急跌的过滤处理
5. 二次急跌
    只在下午交易
    
6. 急跌后连续触发购买信号，需要处理
    avg 15 可以进行调整
'''