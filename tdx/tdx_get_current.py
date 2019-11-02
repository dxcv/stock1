from pytdx.hq import TdxHq_API
import pandas as pd
import time
import sys
import getopt
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
print(rootPath)
sys.path.append(rootPath)

from util.mylogger import logger

api = TdxHq_API()

pd.set_option('display.max_columns', None)


def is_trading_hour():
    current_time = time.strftime("%H:%M:%S", time.localtime())
    return (current_time >= '09:30' and current_time <= '11:30') or (
            current_time >= '13:00' and current_time <= '15:00')


def execute_query(api):
    """
    执行查询
    :param api:
    :return:
    """
    logger.info("get_security_quotes start ")
    start = time.time()
    data = api.get_security_quotes([(0, '000001'), (1, '600300')])
    end = time.time()
    logger.info("get_security_quotes finished, cost=" + str(int((end - start) * 1000)) + "ms")
    data_df = api.to_df(data)

    display_columns = [
        'code',
        'reversed_bytes0',
        'active1',
        'price',
        'last_close',
    ]

    logger.info("\r\n" + str(data_df[display_columns]))


def loop_query(ip, pause_second, force_loop):
    """
    轮训
    """

    if api.connect(ip, 7709):
        logger.info("connected. ip=%s, pause_second=%ss start loop query " % (ip, pause_second))
        while True:

            # 非强制模型下（正常情况），不是交易时间停止查询
            if force_loop is False and is_trading_hour() is False:
                time.sleep(10)
                return

            execute_query(api)

            time.sleep(pause_second)

        api.disconnect()
        logger.info("disconnected...  ")
    else:
        logger.info("connect %s failed." % ip)


if __name__ == '__main__':

    ip = '119.147.212.81'  # 默认轮训服务器地址
    second = 0.5  # 500ms一次轮训
    force_loop = False  # 非强制查询的时候会在停盘期间停止轮训
    opts, args = getopt.getopt(sys.argv[1:], '-i:-s:-f')
    for opt_name, opt_value in opts:
        if opt_name == '-i':
            ip = opt_value
        if opt_name == '-s':
            second = int(opt_value)
        if opt_name == '-f':
            force_loop = True

    while True:
        try:
            logger.info("start loop query")
            loop_query(ip, second, force_loop)
            time.sleep(1)
            logger.info("finish loop query")
        except Exception as e:
            logger.error("something wrong...", e)
