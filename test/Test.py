from pylab import *
import data.ReadCSV as rc
import pandas as pd
import numpy as np
import util.jwdata as jd


# pfyh = jd.get_price_panel(['600000.SH'], '20190603', '20190613')

# pfyh = jd.get_price_panel(['600000.SH'], self.backtest_start_date, self.backtest_end_date)
# pfyh = pfyh['close', :, :]['600000.SH']
# (pfyh / pfyh[0]).plot(label="600000.SH", style='r-*')
# plt.show()

# df = rc.get_fast_down_time('2019-06-03', '600000.SH', 15, 2, -0.5)

# print(df)


df1 = rc.get_fast_down_time('2019-06-03', '600000.SH', 15 , 2, -0.3)

for code in jd.get_hs300_codes():

    df2 = rc.get_fast_down2('2019-06-10', code, 10 , 2, -2)
    if len(df2) <= 0:
        continue

    print(code)
    print(df2)

# print(df1)

df2 = rc.get_data('600000.SH')

df2 = df2[df2['date'] == '2019-06-03'][['close']]

res = pd.concat([rc.get_ma(df2['close'], 15), rc.get_ma(df2['close'], 2)], join='inner', axis=1)

res.plot()
plt.show()