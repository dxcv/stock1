import util.jwtrade as jt
import alpha.Alpha191_3 as ap
import numpy as np
import util.jwdata as jd
import data.ReadCSV as rc
import datetime

def daily_callback(ctx):
    date = ctx.current_day

    # hs300 = ['002470.SZ']

    # 先卖空
    code = '600000.SH'

    f_date = (datetime.datetime.strptime(date, "%Y%m%d")).strftime('%Y-%m-%d')

    open_df = rc.get_data(code)
    open_df = open_df[open_df['date'] == f_date]
    open = open_df.head(1)['open'][0]
    ctx.order_target_value(code, open, 0)


    time_df = rc.get_fast_down_time(f_date, code, 15, 2, -0.3)

    if time_df is not None and len(time_df) >= 0:
        for i in range(len(time_df)):

            print(f_date,time_df.iloc[i]['datetime'], time_df.iloc[i]['c_ma2'])

            ctx.order_target_value(code, time_df.iloc[i]['c_ma2'], 100000)

    return

if __name__ == '__main__':

    t = jt.Trade(backtest_start_date='20190603', backtest_end_date='20190830', try_all=True)

    t.run_daily(daily_callback)

    print(t.daily_capital)

    t.show()
