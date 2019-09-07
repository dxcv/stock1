import util.JWDataFromTushare as jdt
import util.JWDataFromDB as jdd
import pandas as pd


# code = '000063.SZ'
code = '600000.SH'
start = '20190601'
end = '20190630'

df1 = jdt.get_price(code, start, end)
df2 = jdd.get_price(code, start, end)


for item in ['close', 'open', 'high', 'low', 'pre_close']:
    print("\r\n diff %s:"%item)
    diff_df = pd.DataFrame({'c1':df1[item], 'c2':df2[item]})
    print(diff_df[diff_df['c1'] != diff_df['c2']])