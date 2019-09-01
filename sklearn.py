import pandas as pd
import tushare as ts

from sklearn import linear_model

# 设置tushare pro的token并获取连接
ts.set_token('d3fdbde82434cd6d7897550852136449f9fcba912e3eacb47b004600')
pro = ts.pro_api()

# 股票日线
# df = ts.pro_bar(ts_code='000002.SZ', adj='hfq', start_date='20170601', end_date='20190615')
df = ts.pro_bar(ts_code='000002.SZ', adj='qfq', start_date='20190501', end_date='20190515')

# 指数日线
# df = pro.index_daily(ts_code='000001', start_date='20180101', end_date='20181011')

# print(list(df.index)[1:])


pre_vol = []
pre3_chg = []
i = 0
for x in list(df['vol']):
    if i == 0:
        pre_vol.append(0)
    else:
        #         pre_vol.append(float(df['vol'][i-1])/10000)
        pre_vol.append(df['vol'][i - 1] / 10000)

    if i <= 2:
        pre3_chg.append(0)
    else:
        pre3_chg.append(float(df['change'][i - 1]) + float(df['change'][i - 2]) + float(df['change'][i - 3]))

    i += 1

df['pre_vol'] = pd.Series(pre_vol, index=list(df.index))
df['pre3_chg'] = pd.Series(pre3_chg, index=list(df.index))

# print(df.values)
# print(df[['change','pre_vol','pre3_chg']][3:])

print(df[['pre_vol', 'pre3_chg', 'change']][3:])

arr = df[['pre_vol', 'pre3_chg', 'change']][3:].values

print(arr)

X = arr[:, :-1]
Y = arr[:, -1]

print(Y)

# # 建立模型
regr = linear_model.LinearRegression()

# # # 训练数据
regr.fit(X, Y)

# # # 拿到相关系数
print('coefficients(b1,b2...):', regr.coef_)
print('intercept(b0):', regr.intercept_)

# # # 评估模型
print("score0=" + str(regr.score(X, Y)))

# change_list = np.array([float(i) for i in list(df['change'])[::-1]]).reshape(-1,1)
# vol_list = np.array([float(i/10000) for i in list(df['vol'])[::-1]]).reshape(-1,1)

# # print(change_list)
# # print(vol_list)

# lr = linear_model.LinearRegression()

# lr.fit(vol_list, change_list)

# print(lr.score(vol_list, change_list))
# print(lr.coef_)
# print(lr.intercept_)

# f = lr.coef_[0] * vol_list + lr.intercept_

# plt.scatter(vol_list, change_list)
# plt.plot(vol_list, f, color='r', label='predit')
# plt.show()
