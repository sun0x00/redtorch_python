# coding=utf-8

import operator
from qtpy.QtCore import *
from qtpy import QtGui, QtCore, QtWidgets
from redtorch.trader.language import text
from redtorch.trader.language import constant
from redtorch.trader.gateway import dynamicGatewayList
import time


class ConnectionManagerDialog(QtWidgets.QDialog):
    """连接管理器窗口"""

    def __init__(self, mainEngine, dataList=None, *args):
        """Constructor"""
        QtWidgets.QDialog.__init__(self, *args)

        self.mainEngine = mainEngine

        if mainEngine is None:
            if dataList is None:
                dataList = []
            else:
                dataList = dataList
        else:
            dataList = self.loadDataListFromDB()

        # 表头
        self.dataHeader = [text.GATEWAY_NAME,
                           text.CONNECT_STATUS,
                           text.USER_ID,
                           text.BROKER_ID,
                           text.GATEWAY_MODULE,
                           text.TD_ADDRESS,
                           text.MD_ADDRESS,
                           text.GATEWAY_DISPLAY_NAME]
        # 定位
        self.setGeometry(0, 0, 1120, 600)
        self.move(QtWidgets.QDesktopWidget().availableGeometry().center() - self.frameGeometry().center())
        # 窗口标题
        self.setWindowTitle(text.CONNECTION_MANAGER)
        # 数据
        self.tableModel = ConnectionTableModel(self, dataList, self.dataHeader)
        self.tableView = QtWidgets.QTableView()
        self.tableView.setModel(self.tableModel)
        # 表格不允许选中
        self.tableView.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.tableView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableView.setFocusPolicy(Qt.NoFocus)
        # 绑定事件
        self.tableView.clicked.connect(self.showSelection)
        self.tableView.clicked.connect(self.selectRow)
        self.tableView.doubleClicked.connect(self.rowDoubleClicked)
        # 控制排序
        self.tableView.setSortingEnabled(False)
        # 交替颜色
        self.tableView.setAlternatingRowColors(True)

        # 表头自适应等宽度
        # tableViewHeader = self.tableView.horizontalHeader()
        # for i in range(0, len(self.dataHeader)):
        #     tableViewHeader.setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        # 逐列设置宽度
        self.tableView.setColumnWidth(0, 140)
        self.tableView.setColumnWidth(1, 70)
        self.tableView.setColumnWidth(2, 90)
        self.tableView.setColumnWidth(3, 70)
        self.tableView.setColumnWidth(4, 170)
        self.tableView.setColumnWidth(5, 190)
        self.tableView.setColumnWidth(6, 190)
        self.tableView.setColumnWidth(7, 150)

        # 表格布局
        tableVBoxLayout = QtWidgets.QVBoxLayout()
        tableVBoxLayout.addWidget(self.tableView)

        # 创建添加按钮
        self.selectAllButton = QtWidgets.QPushButton(text.SELECT_ALL)
        self.selectReverseButton = QtWidgets.QPushButton(text.SELECT_REVERSE)
        self.deleteSelectedButton = QtWidgets.QPushButton(text.DELETE_SELECTED)
        self.addButton = QtWidgets.QPushButton(text.ADD)
        self.connectSelectedButton = QtWidgets.QPushButton(text.CONNECT_SELECTED)
        self.connectAllButton = QtWidgets.QPushButton(text.CONNECT_ALL)
        self.disconnectSelectedButton = QtWidgets.QPushButton(text.DISCONNECT_SELECTED)
        self.disconnectAllButton = QtWidgets.QPushButton(text.DISCONNECT_ALL)

        # 按钮布局
        buttonGridLayout = QtWidgets.QGridLayout()
        buttonGridLayout.addWidget(self.selectAllButton, 0, 1)
        buttonGridLayout.addWidget(self.selectReverseButton, 0, 2)
        buttonGridLayout.addWidget(self.deleteSelectedButton, 0, 3)
        buttonGridLayout.addWidget(self.addButton, 0, 4)
        buttonGridLayout.addWidget(self.connectSelectedButton, 0, 5)
        buttonGridLayout.addWidget(self.connectAllButton, 0, 6)
        buttonGridLayout.addWidget(self.disconnectSelectedButton, 0, 7)
        buttonGridLayout.addWidget(self.disconnectAllButton, 0, 8)


        # 按钮绑定事件
        self.selectAllButton.clicked.connect(self.selectAll)
        self.selectReverseButton.clicked.connect(self.selectReverse)
        self.deleteSelectedButton.clicked.connect(self.deleteSelected)
        self.addButton.clicked.connect(self.add)
        self.connectSelectedButton.clicked.connect(self.connectSelected)
        self.connectAllButton.clicked.connect(self.connectAll)
        self.disconnectSelectedButton.clicked.connect(self.disconnectSelected)
        self.disconnectAllButton.clicked.connect(self.disconnectAll)

        # 布局
        layout = QtWidgets.QGridLayout(self)

        # 整合布局
        layout.addLayout(tableVBoxLayout, 0, 0)
        layout.addLayout(buttonGridLayout, 1, 0)
        self.setLayout(layout)

    def contextMenuEvent(self, event):
        pos = self.tableView.viewport().mapFrom(self, event.pos())
        tableViewIndex = self.tableView.indexAt(pos)

        # 单独测试时定位
        # tableViewIndex = self.tableView.indexAt(event.pos())

        if tableViewIndex.row() != -1 and tableViewIndex.column() != -1:
            changeConnectStateAction = QtWidgets.QAction('连接/断开', self)
            changeConnectStateAction.triggered.connect(lambda: self.changeConnectState(tableViewIndex))

            editAction = QtWidgets.QAction('编辑', self)
            editAction.triggered.connect(lambda: self.edit(tableViewIndex))

            deleteAction = QtWidgets.QAction('删除', self)
            deleteAction.triggered.connect(lambda: self.delete(tableViewIndex))

            menu = QtWidgets.QMenu(self.tableView)
            menu.addAction(changeConnectStateAction)
            menu.addAction(editAction)
            menu.addAction(deleteAction)
            menu.exec_(self.mapToGlobal(event.pos()))

    def loadDataListFromDB(self):
        try:
            accountList = self.mainEngine.dbQuery(constant.RED_TORCH_DB_NAME, 'account_collection', {})
            dataList = list()

            for account in accountList:
                data = list()

                gatewayName = str(account['_id'])
                tmpCheckBox = QtWidgets.QCheckBox(gatewayName)
                data.append(tmpCheckBox)

                gateway = self.mainEngine.getGateway(gatewayName)
                if gateway is None:
                    data.append(text.CONNECT_OFF)
                elif not gateway.isMdConnected() or not gateway.isTdConnected():
                    data.append(text.CONNECT_OFF)
                else:
                    data.append(text.CONNECT_ON)

                data.append(str(account['userID']))
                data.append(str(account['brokerID']))
                data.append(str(account['gatewayModule']))
                data.append(str(account['tdAddress']))
                data.append(str(account['mdAddress']))
                data.append(str(account['gatewayDisplayName']))
                dataList.append(data)

            dataList = dataList
        except Exception as e:
            print(e)
            dataList = []

        return dataList

    def updateModel(self, dataList, dataHeader):

        self.tableModel = ConnectionTableModel(self, dataList, dataHeader)
        self.tableView.setModel(self.tableModel)
        self.tableView.update()

    def showSelection(self, item):

        cellContent = item.data()
        print(u">>> you clicked on {}".format(cellContent))

    def selectRow(self, index):

        if self.tableModel.dataList[index.row()][0].isChecked():
            self.tableModel.setData(self.tableModel.createIndex(index.row(), 0), QtCore.Qt.Unchecked,
                                    QtCore.Qt.CheckStateRole)
        else:
            self.tableModel.setData(self.tableModel.createIndex(index.row(), 0), QtCore.Qt.Checked,
                                    QtCore.Qt.CheckStateRole)

    def rowDoubleClicked(self, index):

        if self.tableModel.dataList[index.row()][0].isChecked():
            self.tableModel.setData(self.tableModel.createIndex(index.row(), 0), QtCore.Qt.Unchecked,
                                    QtCore.Qt.CheckStateRole)
        else:
            self.tableModel.setData(self.tableModel.createIndex(index.row(), 0), QtCore.Qt.Checked,
                                    QtCore.Qt.CheckStateRole)

        self.edit(index)

    def selectAll(self):

        for data in self.tableModel.dataList:
            data[0].setChecked(True)
        self.tableModel.updateModel(self.tableModel.dataList)

    def selectReverse(self):

        for data in self.tableModel.dataList:
            if data[0].isChecked():
                data[0].setChecked(False)
            else:
                data[0].setChecked(True)
        self.tableModel.updateModel(self.tableModel.dataList)

    def add(self):
        """增加"""
        # 弹窗
        dialog = EditDialog()
        if dialog.exec_():

            # 获取数据
            data = dialog.getData()
            # 构造mongo ID
            data['_id'] = data['brokerID'] + "_" + data['userID']
            gatewayname = str(data['_id'])
            # 先根据ID查询记录
            accountList = self.mainEngine.dbQuery(constant.RED_TORCH_DB_NAME, 'account_collection',
                                                  {'_id': data['_id']})

            # 判断是否存在
            if len(accountList) > 0:

                quitMsg = u"记录已存在，是否覆盖?"
                # 弹框询问是否覆盖
                reply = QtWidgets.QMessageBox.question(self, text.WARN, quitMsg, QtWidgets.QMessageBox.Yes,
                                                       QtWidgets.QMessageBox.No)
                # 如果是则覆盖，否则忽略数据
                if reply == QtWidgets.QMessageBox.Yes:
                    self.mainEngine.dbUpdate(constant.RED_TORCH_DB_NAME, 'account_collection', data,
                                             {'_id': data['_id']})
            else:

                # 如果不存在直接插入
                self.mainEngine.dbInsert(constant.RED_TORCH_DB_NAME, 'account_collection', data)

            # 判断用户是否点击了保存并连接
            if dialog.getSaveAndConnectFlag():
                self.gatewayConnect(gatewayname)
                self.setCursor(Qt.WaitCursor)
                time.sleep(1.5)
                self.setCursor(Qt.ArrowCursor)

        # 销毁实例
        dialog.destroy()

        dataList = self.loadDataListFromDB()
        self.tableModel.updateModel(dataList)

    def connectSelected(self):
        for data in self.tableModel.dataList:
            if data[0].isChecked():
                self.gatewayConnect(data[0].text())
                
        self.setCursor(Qt.WaitCursor)
        time.sleep(1.5)
        self.setCursor(Qt.ArrowCursor)
        dataList = self.loadDataListFromDB()
        self.tableModel.updateModel(dataList)

    def connectAll(self):
        for data in self.tableModel.dataList:
            self.gatewayConnect(data[0].text())
        self.setCursor(Qt.WaitCursor)
        time.sleep(1.5)
        self.setCursor(Qt.ArrowCursor)
        dataList = self.loadDataListFromDB()
        self.tableModel.updateModel(dataList)

    def disconnectSelected(self):
        for data in self.tableModel.dataList:
            if data[0].isChecked():
                gatewayName = data[0].text()
                if self.checkGatewayConnectState(gatewayName):
                    gateway = self.mainEngine.getGateway(gatewayName)
                    gateway.close()
                    self.mainEngine.removeGateway(gatewayName)

        dataList = self.loadDataListFromDB()
        self.tableModel.updateModel(dataList)

    def disconnectAll(self):
        for data in self.tableModel.dataList:
            gatewayName = data[0].text()
            if self.checkGatewayConnectState(gatewayName):
                gateway = self.mainEngine.getGateway(gatewayName)
                gateway.close()
                self.mainEngine.removeGateway(gatewayName)

        dataList = self.loadDataListFromDB()
        self.tableModel.updateModel(dataList)

    def edit(self, index):
        """编辑"""

        gatewayName = self.tableModel.dataList[index.row()][0].text()
        accountList = self.mainEngine.dbQuery(constant.RED_TORCH_DB_NAME, 'account_collection', {'_id': gatewayName})
        if len(accountList) == 0:
            QtWidgets.QMessageBox.information(self, text.INFO, u'记录不存在', QtWidgets.QMessageBox.Ok)
        else:
            data = accountList[0]
            gatewayName = data['brokerID'] + "_" + data['userID']

            if self.checkGatewayConnectState(gatewayName):
                reply = QtWidgets.QMessageBox.question(self, text.WARN, u'修改将会断开连接，请确认？', QtWidgets.QMessageBox.Yes,
                                                       QtWidgets.QMessageBox.No)
                # 如果是则覆盖，否则忽略数据
                if reply == QtWidgets.QMessageBox.Yes:
                    gateway = self.mainEngine.getGateway(gatewayName)
                    gateway.close()
                else:
                    return

            self.mainEngine.removeGateway(gatewayName)

            # 弹出编辑窗
            dialog = EditDialog(edit=True, data=data, parent=self)
            if dialog.exec_():
                data = dialog.getData()
                data['_id'] = gatewayName
                self.mainEngine.dbUpdate(constant.RED_TORCH_DB_NAME, 'account_collection', data, {'_id': data['_id']})

                if dialog.getSaveAndConnectFlag():
                    self.gatewayConnect(gatewayName)
                    self.setCursor(Qt.WaitCursor)
                    time.sleep(1.5)
                    self.setCursor(Qt.ArrowCursor)
            dialog.destroy()

        dataList = self.loadDataListFromDB()
        self.tableModel.updateModel(dataList)

    def delete(self, index):

        reply = QtWidgets.QMessageBox.warning(self, text.WARN, u'删除将断开已连接的接口，确定删除？',
                                              QtWidgets.QMessageBox.Yes,
                                              QtWidgets.QMessageBox.No)
        # 如果是则覆盖，否则忽略数据
        if reply == QtWidgets.QMessageBox.Yes:
            gatewayName = self.tableModel.dataList[index.row()][0].text()
            self.mainEngine.dbDelete(constant.RED_TORCH_DB_NAME, 'account_collection', {'_id': gatewayName})

            if self.checkGatewayConnectState(gatewayName):
                gateway = self.mainEngine.getGateway(gatewayName)
                gateway.close()

            self.mainEngine.removeGateway(gatewayName)

            dataList = self.loadDataListFromDB()
            self.tableModel.updateModel(dataList)

    def deleteSelected(self):

        reply = QtWidgets.QMessageBox.warning(self, text.WARN, u'删除将断开已连接的接口，确定删除？',
                                              QtWidgets.QMessageBox.Yes,
                                              QtWidgets.QMessageBox.No)
        # 如果是则覆盖，否则忽略数据
        if reply == QtWidgets.QMessageBox.Yes:
            for data in self.tableModel.dataList:
                if data[0].isChecked():
                    gatewayName = data[0].text()
                    self.mainEngine.dbDelete(constant.RED_TORCH_DB_NAME, 'account_collection', {'_id': gatewayName})

                    if self.checkGatewayConnectState(gatewayName):
                        gateway = self.mainEngine.getGateway(gatewayName)
                        gateway.close()

                    self.mainEngine.removeGateway(gatewayName)

            dataList = self.loadDataListFromDB()
            self.tableModel.updateModel(dataList)

    def checkGatewayConnectState(self, gatewayName):
        gateway = self.mainEngine.getGateway(gatewayName)
        if gateway is None:
            return False
        if not gateway.isMdConnected() or not gateway.isTdConnected():
            return False

        return True

    def gatewayConnect(self, gatewayName):
        gateway = self.mainEngine.getGateway(gatewayName)
        if gateway is None:
            accountList = self.mainEngine.dbQuery(constant.RED_TORCH_DB_NAME, 'account_collection',
                                                  {'_id': gatewayName})
            if len(accountList) != 0:
                account = accountList[0]

                # 使用str方法防止后续API产生错误
                gatewayModule = str(account['gatewayModule'])
                gatewayName = str(account['_id'])
                gatewayDisplayName = str(account['gatewayDisplayName'])
                userID = str(account['userID'])
                password = str(account['password'])
                brokerID = str(account['brokerID'])
                tdAddress = str(account['tdAddress'])
                mdAddress = str(account['mdAddress'])
                if '' == str(account['authCode']):
                    authCode = None
                else:
                    authCode = str(account['authCode'])

                if '' == str(account['userProductInfo']):
                    userProductInfo = None
                else:
                    userProductInfo = str(account['userProductInfo'])

                self.mainEngine.addDynamicGateway(gatewayModule, gatewayName, gatewayDisplayName, userID, password,
                                                  brokerID, tdAddress, mdAddress, authCode=authCode,
                                                  userProductInfo=userProductInfo)

                gateway = self.mainEngine.getGateway(gatewayName)
                if gateway is not None:
                    gateway.connect()

        elif not gateway.isMdConnected() or not gateway.isTdConnected():
            gateway.connect()

    def changeConnectState(self, index):

        gatewayName = self.tableModel.dataList[index.row()][0].text()
        if self.checkGatewayConnectState(gatewayName):
            gateway = self.mainEngine.getGateway(gatewayName)
            gateway.close()

            self.mainEngine.removeGateway(gatewayName)

        else:
            self.gatewayConnect(gatewayName)

        self.setCursor(Qt.WaitCursor)
        time.sleep(1.5)
        self.setCursor(Qt.ArrowCursor)
        dataList = self.loadDataListFromDB()
        self.tableModel.updateModel(dataList)


class ConnectionTableModel(QAbstractTableModel):
    """连接表格模型"""

    def __init__(self, parent, dataList, dataHeader, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.dataList = dataList
        self.dataHeader = dataHeader

    def setDataList(self, dataList):
        self.dataList = dataList
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def updateModel(self, dataList):
        self.dataList = dataList
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self.dataList)

    def columnCount(self, parent):
        return len(self.dataHeader)

    def data(self, index, role):
        if not index.isValid():
            return None
        if (index.column() == 0):
            value = self.dataList[index.row()][index.column()].text()
        else:
            value = self.dataList[index.row()][index.column()]

        if role == QtCore.Qt.EditRole:
            return value
        elif role == QtCore.Qt.DisplayRole:
            return value
        elif role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                if self.dataList[index.row()][index.column()].isChecked():
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.dataHeader[col]
        return None

    def sort(self, col, order):
        """根据给定的列进行排序"""

        if col != 0:
            self.layoutAboutToBeChanged.emit()
            self.dataList = sorted(self.dataList, key=operator.itemgetter(col))
            if order == Qt.DescendingOrder:
                self.dataList.reverse()
            self.layoutChanged.emit()

    def flags(self, index):
        if not index.isValid():
            return None
        if index.column() == 0:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            if value == QtCore.Qt.Checked:
                self.dataList[index.row()][index.column()].setChecked(True)
            else:
                self.dataList[index.row()][index.column()].setChecked(False)
        else:
            pass
        self.dataChanged.emit(index, index)
        return True


class EditDialog(QtWidgets.QDialog):
    """编辑弹窗"""

    def __init__(self, edit=False, data=None, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        # 保存并连接标记
        self.saveAndConnectFlag = False
        # 窗口大小
        self.setFixedSize(400, 300)
        # 判断新增或者编辑
        if edit:
            self.setWindowTitle(text.EDIT)
        else:
            self.setWindowTitle(text.ADD)

        # 表格布局，用来布局QLabel和QLineEdit
        tableGridLayout = QtWidgets.QGridLayout()

        # 用户ID
        rowNum = 0
        tableGridLayout.addWidget(QtWidgets.QLabel(text.USER_ID), rowNum, 0)
        if edit:
            self.userIDLineEdit = QtWidgets.QLineEdit(data['userID'] if 'userID' in data.keys() else None)
            self.userIDLineEdit.setDisabled(True)
        else:
            self.userIDLineEdit = QtWidgets.QLineEdit()
        self.userIDValidator = QtGui.QRegExpValidator(QtCore.QRegExp('^[a-zA-Z0-9]{4,16}$'))
        self.userIDLineEdit.setValidator(self.userIDValidator)
        tableGridLayout.addWidget(self.userIDLineEdit, rowNum, 1)

        # 密码
        rowNum += 1
        tableGridLayout.addWidget(QtWidgets.QLabel(text.PASSWORD), rowNum, 0)
        if edit:
            self.passwordLineEdit = QtWidgets.QLineEdit(data['password'] if 'password' in data.keys() else None)
        else:
            self.passwordLineEdit = QtWidgets.QLineEdit()
        self.passwordValidator = QtGui.QRegExpValidator(QtCore.QRegExp('^.{4,20}$'))
        self.passwordLineEdit.setValidator(self.passwordValidator)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        tableGridLayout.addWidget(self.passwordLineEdit, rowNum, 1)

        # 授权码
        rowNum += 1
        tableGridLayout.addWidget(QtWidgets.QLabel(text.AUTH_CODE), rowNum, 0)
        if edit:
            self.authCodeLineEdit = QtWidgets.QLineEdit(data['authCode' if 'authCode' in data.keys() else None])
        else:
            self.authCodeLineEdit = QtWidgets.QLineEdit()
        tableGridLayout.addWidget(self.authCodeLineEdit, rowNum, 1)

        # 用户产品信息
        rowNum += 1
        tableGridLayout.addWidget(QtWidgets.QLabel(text.USER_PRODUCT_INFO), rowNum, 0)
        if edit:
            self.userProductInfoLineEdit = QtWidgets.QLineEdit(
                data['userProductInfo'] if 'userProductInfo' in data.keys() else None)
        else:
            self.userProductInfoLineEdit = QtWidgets.QLineEdit()
        tableGridLayout.addWidget(self.userProductInfoLineEdit, rowNum, 1)

        # 经纪商ID
        rowNum += 1
        tableGridLayout.addWidget(QtWidgets.QLabel(text.BROKER_ID), rowNum, 0)
        if edit:
            self.brokerIDLineEdit = QtWidgets.QLineEdit(data['brokerID'] if 'brokerID' in data.keys() else None)
            self.brokerIDLineEdit.setDisabled(True)
        else:
            self.brokerIDLineEdit = QtWidgets.QLineEdit()
        self.brokerIDValidator = QtGui.QRegExpValidator(QtCore.QRegExp('^[a-zA-Z0-9]{4,16}$'))
        self.brokerIDLineEdit.setValidator(self.brokerIDValidator)
        tableGridLayout.addWidget(self.brokerIDLineEdit, rowNum, 1)

        # 网关模块
        rowNum += 1
        tableGridLayout.addWidget(QtWidgets.QLabel(text.GATEWAY_MODULE), rowNum, 0)
        self.gatewayModuleComboBox = QtWidgets.QComboBox()
        if edit:
            self.gatewayModuleComboBox.addItem(data['gatewayModule'] if 'gatewayModule' in data.keys() else None)
            self.gatewayModuleComboBox.setDisabled(True)
        else:
            self.gatewayModuleList = dynamicGatewayList
            self.gatewayModuleComboBox.addItems(self.gatewayModuleList)
        tableGridLayout.addWidget(self.gatewayModuleComboBox, rowNum, 1)

        # 网关显示名称
        rowNum += 1
        tableGridLayout.addWidget(QtWidgets.QLabel(text.GATEWAY_DISPLAY_NAME), rowNum, 0)
        if edit:
            self.gatewayDisplayNameLineEdit = QtWidgets.QLineEdit(
                data['gatewayDisplayName'] if 'gatewayDisplayName' in data.keys() else None)
        else:
            self.gatewayDisplayNameLineEdit = QtWidgets.QLineEdit()

        self.gatewayDisplayNameValidator = QtGui.QRegExpValidator(QtCore.QRegExp('^.{4,16}$'))
        self.gatewayDisplayNameLineEdit.setValidator(self.gatewayDisplayNameValidator)
        tableGridLayout.addWidget(self.gatewayDisplayNameLineEdit, rowNum, 1)

        # 交易地址
        rowNum += 1
        tableGridLayout.addWidget(QtWidgets.QLabel(text.TD_ADDRESS), rowNum, 0)
        if edit:
            self.tdAddressLineEdit = QtWidgets.QLineEdit(data['tdAddress'] if 'tdAddress' in data.keys() else None)
        else:
            self.tdAddressLineEdit = QtWidgets.QLineEdit('tcp://')
        # 验证TCP地址，未考虑端口超过65535的情况
        self.tdAddressValidator = QtGui.QRegExpValidator(QtCore.QRegExp(
            '^(tcp:\/\/)(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(:\d{2,5})$'))
        self.tdAddressLineEdit.setValidator(self.tdAddressValidator)
        tableGridLayout.addWidget(self.tdAddressLineEdit, rowNum, 1)

        # 行情地址
        rowNum += 1
        tableGridLayout.addWidget(QtWidgets.QLabel(text.MD_ADDRESS), rowNum, 0)
        if edit:
            self.mdAddressLineEdit = QtWidgets.QLineEdit(data['mdAddress'] if 'mdAddress' in data.keys() else None)
        else:
            self.mdAddressLineEdit = QtWidgets.QLineEdit('tcp://')
        # 验证TCP地址，未考虑端口超过65535的情况
        self.mdAddressValidator = QtGui.QRegExpValidator(QtCore.QRegExp(
            '^(tcp:\/\/)(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(:\d{2,5})$'))
        self.mdAddressLineEdit.setValidator(self.mdAddressValidator)
        tableGridLayout.addWidget(self.mdAddressLineEdit, rowNum, 1)

        # 创建按钮
        saveButton = QtWidgets.QPushButton(text.SAVE)
        saveAndConnectButton = QtWidgets.QPushButton(text.SAVE_AND_CONNECT)
        cancelButton = QtWidgets.QPushButton(text.CANCEL)

        # 按钮布局
        buttonGridLayout = QtWidgets.QGridLayout()
        buttonGridLayout.addWidget(saveButton, 0, 1)
        buttonGridLayout.addWidget(saveAndConnectButton, 0, 2)
        buttonGridLayout.addWidget(cancelButton, 0, 3)

        # 绑定事件
        saveButton.clicked.connect(self.save)  # 确定
        cancelButton.clicked.connect(self.reject)  # 取消
        saveAndConnectButton.clicked.connect(self.saveAndConnect)

        # 整合布局
        layout = QtWidgets.QGridLayout(self)
        layout.addLayout(tableGridLayout, 0, 0)
        layout.addLayout(buttonGridLayout, 1, 0)
        self.setLayout(layout)

    def validate(self):
        """验证输入"""
        state = self.userIDValidator.validate(self.userIDLineEdit.text(), 0)[0]
        if state != QtGui.QValidator.Acceptable:
            QtWidgets.QMessageBox.information(self, text.INFO, u'用户ID输入不正确', QtWidgets.QMessageBox.Ok)
            return False

        state = self.passwordValidator.validate(self.passwordLineEdit.text(), 0)[0]
        if state != QtGui.QValidator.Acceptable:
            QtWidgets.QMessageBox.information(self, text.INFO, u'密码输入不正确', QtWidgets.QMessageBox.Ok)
            return False

        state = self.brokerIDValidator.validate(self.brokerIDLineEdit.text(), 0)[0]
        if state != QtGui.QValidator.Acceptable:
            QtWidgets.QMessageBox.information(self, text.INFO, u'经纪商ID输入不正确', QtWidgets.QMessageBox.Ok)
            return False

        state = self.gatewayDisplayNameValidator.validate(self.gatewayDisplayNameLineEdit.text(), 0)[0]
        if state != QtGui.QValidator.Acceptable:
            QtWidgets.QMessageBox.information(self, text.INFO, u'网关显示名称输入不正确', QtWidgets.QMessageBox.Ok)
            return False

        state = self.tdAddressValidator.validate(self.tdAddressLineEdit.text(), 0)[0]
        if state != QtGui.QValidator.Acceptable:
            QtWidgets.QMessageBox.information(self, text.INFO, u'交易服务器地址输入不正确', QtWidgets.QMessageBox.Ok)
            return False

        state = self.mdAddressValidator.validate(self.mdAddressLineEdit.text(), 0)[0]
        if state != QtGui.QValidator.Acceptable:
            QtWidgets.QMessageBox.information(self, text.INFO, u'行情服务器地址输入不正确', QtWidgets.QMessageBox.Ok)
            return False
        return True

    def save(self):
        """保存"""
        if self.validate():
            self.accept()

    def saveAndConnect(self):
        """保存并连接"""
        if self.validate():
            self.saveAndConnectFlag = True
            self.accept()

    def getSaveAndConnectFlag(self):
        """获取保存并连接标记"""
        return self.saveAndConnectFlag

    def getData(self):
        """获取数据"""
        return {
            'userID': self.userIDLineEdit.text(),
            'password': self.passwordLineEdit.text(),
            'authCode': self.authCodeLineEdit.text(),
            'userProductInfo': self.userProductInfoLineEdit.text(),
            'brokerID': self.brokerIDLineEdit.text(),
            'gatewayModule': self.gatewayModuleComboBox.currentText(),
            'gatewayDisplayName': self.gatewayDisplayNameLineEdit.text(),
            'tdAddress': self.tdAddressLineEdit.text(),
            'mdAddress': self.mdAddressLineEdit.text(),
        }


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    checkbox1 = QtWidgets.QCheckBox("4200_058176")
    checkbox1.setChecked(True)
    testDataList = [
        [checkbox1, text.CONNECT_ON, '058176000', '4200', 'dynamicCtpGateway', 'tcp://111.123.213.001:12345',
         'tcp://111.123.213.001:12345', 'CTP058176'],
        [QtWidgets.QCheckBox("4200_058176"), text.CONNECT_ON, '058176000', '4200', 'dynamicCtpGateway',
         'tcp://111.123.213.001:12345', 'tcp://111.123.213.001:12345', '产品1号0032'],
        [QtWidgets.QCheckBox("4200_058176"), text.CONNECT_ON, '058176000', '4200', 'dynamicCtpGateway',
         'tcp://111.123.213.001:12345', 'tcp://111.123.213.001:12345', '产品1号0032'],
        [QtWidgets.QCheckBox("4200_058176"), text.CONNECT_ON, '058176000', '4200', 'dynamicCtpGateway',
         'tcp://111.123.213.001:12345', 'tcp://111.123.213.001:12345', '产品1号0032'],
        [QtWidgets.QCheckBox("4200_058176"), text.CONNECT_ON, '058176000', '4200', 'dynamicCtpGateway',
         'tcp://111.123.213.001:12345', 'tcp://111.123.213.001:12345', '产品2号0032'],
        [QtWidgets.QCheckBox("4200_058176"), text.CONNECT_ON, '058176000', '4200', 'dynamicCtpGateway',
         'tcp://111.123.213.001:12345', 'tcp://111.123.213.001:12345', '产品1号0032'],
        [QtWidgets.QCheckBox("4200_058176"), text.CONNECT_ON, '058176000', '4200', 'dynamicCtpGateway',
         'tcp://111.123.213.001:12345', 'tcp://111.123.213.001:12345', '产品10号0032']
    ]

    # data = {
    #     'userID': '95954',
    #     'password': "123456",
    #     'authCode': "1233",
    #     'userProductInfo': "123456",
    #     'brokerID': "4200",
    #     'gatewayModule': "gateway",
    #     'gatewayDisplayName': u"测试",
    #     'tdAddress': "tcp://123.123.123.123:12",
    #     'mdAddress': "tcp://123.123.123.123:12"
    # }

    win = ConnectionManagerDialog(None, dataList=testDataList)
    win.show()
    app.exec_()
