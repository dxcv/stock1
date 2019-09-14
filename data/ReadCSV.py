import pandas as pd
from pylab import *

data_dict = {}

def get_ma(df, window):
    ma = df.rolling(window=window).mean()
    ma = ma.dropna()
    return pd.DataFrame({'ma'+str(window): ma.values}, index=ma.index.values)

def get_data(code):
    # 获取某一天的分钟数据

    df = data_dict.get(code)
    if df is None:
        df = pd.read_csv('D:\\export\\'+code, dtype={'time':str}, sep = ",")
        data_dict[code] = df

    df['datetime'] = df['date'] + ' ' + df['time']

    df.set_index('datetime', drop=True, inplace=True)

    return df


def get_fast_down_time(date, code, pre_window = 15, compare_window = 2, down_pct = -0.2):

    pre_ma_col = 'ma'+str(pre_window)
    comp_ma_col = 'ma'+str(compare_window)

    p_pre_ma_col = 'p_' + pre_ma_col
    c_comp_ma_col = 'c_' + comp_ma_col

    # 获取某一天的分钟数据
    df = get_data(code)

    df = df[df['date'] == date]['close']

    # 计算分钟ma数据
    res = pd.concat([get_ma(df, pre_window), get_ma(df, compare_window)], join='inner', axis=1)

    indexs = res.index.values
    df2 = pd.DataFrame([], columns=['datetime',c_comp_ma_col, p_pre_ma_col])
    for i in range(0, len(res)):

        if i < compare_window:
            continue

        c_ma2 = res.iloc[i][comp_ma_col]
        p_ma15 = res.iloc[i-compare_window][pre_ma_col]

        tmp_df = pd.DataFrame([[indexs[i], c_ma2, p_ma15]], columns=['datetime',c_comp_ma_col, p_pre_ma_col])

        df2 = df2.append(tmp_df)

    # 计算当前2分钟平均与2分钟之前N分钟平均的变化
    df2['pct'] = (df2[c_comp_ma_col] - df2[p_pre_ma_col])*100 / df2[p_pre_ma_col]

    # 按照跌幅排序
    # df2 = df2.sort_values(by='pct', ascending = True)

    # 选择急跌时机
    df2 = df2[df2['pct'] < down_pct]

    return df2


def get_fast_down2(date, code, pre_window = 15, compare_window = 2, down_pct = -0.2):

    pre_ma_col = 'ma'+str(pre_window)
    comp_ma_col = 'ma'+str(compare_window)

    # 获取某一天的分钟数据
    df = get_data(code)

    df = df[df['date'] == date]['close']

    # 计算分钟ma数据
    res = pd.concat([get_ma(df, pre_window), get_ma(df, compare_window)], join='inner', axis=1)

    res['pct'] = (res[comp_ma_col] - res[pre_ma_col])*100 / res[pre_ma_col]

    res = res[res['pct'] < down_pct]

    return res

