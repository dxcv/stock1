import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 创建 handler 输出到文件
handler = logging.FileHandler("file.log", mode='w')
handler.setLevel(logging.INFO)

# handler 输出到控制台
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# 创建 logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(handler)
logger.addHandler(ch)