# encoding: UTF-8

# 重载sys模块，设置默认字符串编码方式为utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# vn.trader模块
from redtorch.event import EventEngine2
from redtorch.trader.uiQt import qApp

# 加载上层应用
from redtorch.trader.app import ctaStrategy
from redtorch.trader.app import riskManager
from redtorch.trader.vtEngine import MainEngine
from redtorch.trader.uiMainWindow import MainWindow


#----------------------------------------------------------------------
def main():
    """主程序入口"""
    # 创建事件引擎
    ee = EventEngine2()

    # 创建主引擎
    me = MainEngine(ee)

    # 添加上层应用
    me.addApp(riskManager)
    me.addApp(ctaStrategy)

    # 创建主窗口
    mw = MainWindow(me, ee)
    mw.showMaximized()

    # 在主线程中启动Qt事件循环
    sys.exit(qApp.exec_())


if __name__ == '__main__':
    main()

