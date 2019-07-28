import tushare as ts
import pandas as pd
import seaborn as sns
import Constants as const



ts.set_token(const.TUSHARE_TOKEN)
pro = ts.pro_api()


price = ts.pro_bar(ts_code='000001.SZ', adj='qfq', start_date='20190610', end_date='20190625')

pct_chg = price['pct_chg'].dropna()

sns.distplot(pct_chg)
