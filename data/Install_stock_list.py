from sqlalchemy import create_engine
import util.JWDataFromTushare as jdt
import pandas as pd

import pymysql
pymysql.install_as_MySQLdb()

'''
导入股票列表脚本
'''

engine = create_engine('mysql://root:admin@127.0.0.1/my_stock?charset=utf8')

list = jdt.get_stock_list();

list.to_sql('stock_list', engine, if_exists='replace', index=False)

print("import done！total=", len(list))
