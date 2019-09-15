from pylab import *
import data.ReadCSV as rc
import pandas as pd
import numpy as np
import util.jwdata as jd


codes =['600111.SH', '600115.SH', '600118.SH', '600153.SH', '600170.SH', '002415.SZ']
# codes =['600115.SH']
date = '2019-06-03'

show_df = pd.DataFrame([], columns=codes)

for code in codes:
    df2 = rc.get_data(code)
    df2 = df2[df2['date'] == date][['close']]

    ma_df = pd.concat([rc.get_ma(df2['close'], 10), rc.get_ma(df2['close'], 1)], join='inner', axis=1)

    diff = (ma_df['ma1'] - ma_df['ma10']) * 1000 / ma_df['ma10']

    show_df[code] = diff.values

    print(code, 'std=', diff.std(), 'mean=', diff.mean())

# print(show_df)

# print(show_df[codes[0]].std())

# show_df.plot()

# df['diff'].plot()

# 展示
# plt.grid(axis="both", linestyle='--')
# plt.legend()
# plt.show()


fig, ax = plt.subplots(2, 3)
# # make a little extra space between the subplots
# fig.subplots_adjust(hspace=0.5)
#
ax[0, 0].plot(show_df[codes[0]])
ax[0, 0].set_title(codes[0], fontsize=10)

ax[0, 1].plot(show_df[codes[1]])
ax[0, 1].set_title(codes[1], fontsize=10)

ax[0, 2].plot(show_df[codes[2]])
ax[0, 2].set_title(codes[2], fontsize=10)

ax[1, 0].plot(show_df[codes[3]])
ax[1, 0].set_title(codes[3], fontsize=10)

ax[1, 1].plot(show_df[codes[4]])
ax[1, 1].set_title(codes[4], fontsize=10)

ax[1, 2].plot(show_df[codes[5]])
ax[1, 2].set_title(codes[5], fontsize=10)

plt.show()
