import tushare as ts

ts.set_token('d3fdbde82434cd6d7897550852136449f9fcba912e3eacb47b004600')
pro = ts.pro_api()


'''
    获取股票日线数据（默认前复权）
'''
def get_price(code=None, start_date=None, end_date=None):

    df = ts.pro_bar(ts_code=code, adj='qfq', start_date=start_date, end_date=end_date)

    # 设置索引
    df.set_index('trade_date', inplace=True)

    # 按照日期顺序排序
    df = df.sort_values(by='trade_date', ascending=True)

    return df


'''
    获取股票列表
'''
def get_stock_list():

    list = pro.stock_basic(fields='ts_code,symbol,name,area,industry,list_status,list_date')
    return list