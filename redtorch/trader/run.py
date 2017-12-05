# encoding: UTF-8

# 重载sys模块，设置默认字符串编码方式为utf8
import sys
import logging

from vtFunction import *
loggingFormatStr = '[%(asctime)s]-[P:%(process)d]-[T:%(thread)d]-[%(levelname)s]-[%(filename)s]-[%(funcName)s]-[line: %(lineno)d]-[%(message)s]'
# 日志记录到文件
logFileName = filename = 'redtorch_' + datetime.now().strftime('%Y%m%d') + '.log'
logging.basicConfig(filename=getTempPath(logFileName), level=logging.DEBUG, format=loggingFormatStr)
# 控制台同样打印日志
consoleLoggingFormatter = logging.Formatter(loggingFormatStr)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(consoleLoggingFormatter)
logging.getLogger('').addHandler(consoleHandler)


reload(sys)
sys.setdefaultencoding('utf8')

# 判断操作系统
import platform

system = platform.system()
# vn.trader模块
from redtorch.event import EventEngine
from redtorch.trader.vtEngine import MainEngine
from redtorch.trader.uiQt import createQApp
from redtorch.trader.uiMainWindow import MainWindow

# 加载上层应用
from redtorch.trader.app import (riskManager, ctaStrategy, spreadTrading)

# ----------------------------------------------------------------------
def main():
    logging.info("主程序开始启动")
    """主程序入口"""
    # 创建Qt应用对象
    qApp = createQApp()

    # 创建事件引擎
    ee = EventEngine()

    # 创建主引擎
    me = MainEngine(ee)

    # # 添加交易接口
    # me.addDynamicGateway(dynamicCtpGateway)

    # 添加上层应用
    me.addApp(riskManager)
    me.addApp(ctaStrategy)
    me.addApp(spreadTrading)

    # 创建主窗口
    mw = MainWindow(me, ee)
    mw.showMaximized()

    # 在主线程中启动Qt事件循环
    sys.exit(qApp.exec_())


if __name__ == '__main__':
    main()
