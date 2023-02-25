#!/usr/bin/python3
# -*- coding: utf-8 -*-





import os
import re
import sys
import csv
import time
import yaml
import queue
import snap7
import ctypes
import struct
import serial
import sqlite3
import modbus_tk.defines as tkCst
import modbus_tk.modbus_rtu as tkRtu
import modbus_tk.modbus_tcp as modbus_tcp
from PyQt5 import QtCore, QtGui, QtWidgets

from LoginPanel_DesCode import login_M
import About_us
import Cd_subFunction as subCd
import PyCd_subPortConfig as portCfg
import PyCd_subDataQuery_v1 as queryWin

from PyUi_main_v109 import Ui_MainWindow




class c_weighMointor(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(c_weighMointor, self).__init__(parent)

        self.setupUi(self)


        # self.setFixedSize(self.width(), self.height())
        # sub controls visible
        # for ctrl in [self.label_foreWighing, self.tableWidg_exWight, self.label_reWighing, self.tableWidg_reWight,
        #              self.label_result, self.tableWidg_result]:
        #     ctrl.setVisible(False)
        for ctrl in [self.label_result, self.tableWidg_result]:
            ctrl.setVisible(False)
        self.tabWidget.removeTab(1)
        " SerialNumber PlatNumber Order Record_Time exWeight reWeight limitDown limitUp injectionWeight Level"
        column_width = [150, 220, 300, 180, 180]
        for i, column in enumerate(column_width):
            self.tableWid_data.setColumnWidth(i, column)
        self.tableWid_data.setRowCount(0)

        " Create a new folder, save the data"
        parentDir = os.path.split(os.getcwd())[0]
        if not os.path.isdir(os.path.join(parentDir, "data")):
            os.mkdir(os.path.join(parentDir, "data"))
        self.parentDir = os.path.join(parentDir, "data")

        """ user manger """
        self.powerLimit = -1
        self.q_csv = queue.Queue()
        self.ui_powerLimit_display(self.powerLimit)

        "initial default values"
        self.plc_rs485_port = {}
        self.plc_tcp_port = "192.168.10.20"
        self.plc_rack = 0
        self.plc_slot = 1
        self.plc_tcp_stationNo = 0x01
        self.port_linkType = "TCP"
        self.pwr_port_handle = None

        self.defaultParaPath = ""
        self._run_State = False
        self._run_Case = 0
        self.sn_table = 0

        # data statistics
        self.total_value = 0
        self.qualified_value = 0
        self.addLiquid_value = 0
        self.seriesNumber = 0

        "Initialize function"
        self.readDefaultConfig()
        self.slot_updateDataStatistics()
        self.weightMontr_thread = c_mointerThread()
        self.weightMontr_thread.render(self.port_linkType, self.plc_rs485_port, self.plc_tcp_port, self.plc_rack, self.plc_slot)
        self.dataSave_thread = c_dataSavemointerThread()
        self.dataSave_thread.render(self.q_csv)

        """ menu action --> single"""
        self.actionLogin.triggered.connect(self.slot_userLogin)
        self.actionLogout.triggered.connect(self.slot_userLogout)
        self.actionQuit.triggered.connect(self.slot_quitApp)
        self.actionAbout.triggered.connect(self.slot_about)
        self.actionConfig_Port.triggered.connect(self.slot_portSetting)
        self.actionData_Query.triggered.connect(self.slot_Query)

        self.pushB_countClear.clicked.connect(self.slot_countClear)

        # the program hex thread signal and slots
        self.weightMontr_thread.mointer_msgBox.connect(self.showWarnMsgbox, QtCore.Qt.BlockingQueuedConnection)
        self.weightMontr_thread.mointer_weightRead.connect(self.update_eleScaleValue)
        self.weightMontr_thread.mointer_weighingInfo.connect(self.refreshDataTable)
        self.weightMontr_thread.mointer_wghInfo.connect(self.refreshDataTable_2nd)

        self.weightMontr_thread.mointer_S7Info.connect(self.refreshVoltRes)
        self.weightMontr_thread.mointer_S7record.connect(self.refreshVoltResTable)

        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)


    def readDefaultConfig(self):
        self.config_setting = {}
        if os.path.isfile('config.yaml'):
            try:
                with open('config.yaml', 'r') as yamlfile:
                    self.config_setting = yaml.load(yamlfile, Loader=yaml.UnsafeLoader)
            except Exception as err:
                QtWidgets.QMessageBox.critical(self, "Critical",
                                               self.tr("The config.yaml open abnoraml!") + "\n" + str(err))
        else:
            QtWidgets.QMessageBox.critical(self, "Critical", self.tr("The config.yaml don't exist!" + "\n"))

        subCd.readConfig(self.config_setting, self.plc_rs485_port)
        self.port_linkType = self.config_setting.get("Default").get("Link Type", "TCP")
        self.plc_tcp_port = self.config_setting.get("Tcp Port").get("IP address", "192.168.10.20")
        # self.plc_tcp_stationNo = self.config_setting.get("Tcp Port").get("address", 0x01)
        self.plc_rack = self.config_setting.get("Tcp Port").get("rack", 0)
        self.plc_slot = self.config_setting.get("Tcp Port").get("slot", 1)

        self.total_value = self.config_setting.get("Default").get("Total count", 0)
        self.qualified_value = self.config_setting.get("Default").get("Qualified count", 0)
        self.addLiquid_value = self.config_setting.get("Default").get("AddLiquid count", 0)

    def ui_powerLimit_display(self, powerLimit=-1):
        if powerLimit == -1:
            self.actionLogin.setEnabled(True)
            self.actionConfig_Port.setEnabled(False)
            self.actionLogout.setEnabled(False)
            self.actionData_Query.setEnabled(False)

            self.pushB_countClear.setEnabled(False)


        if powerLimit >= 1:
            self.actionLogin.setDisabled(True)
            self.actionLogout.setEnabled(True)
            self.actionConfig_Port.setEnabled(True)
            self.actionData_Query.setEnabled(True)

            self.pushB_countClear.setEnabled(True)

    " menu action slots "
    def slot_userLogin(self):
        self.ui_userLogin = login_M()
        self.ui_userLogin.exec_()

        self.powerLimit = self.ui_userLogin.powerLmt
        self.ui_powerLimit_display(self.powerLimit)

    def slot_userLogout(self):
        self.powerLimit = -1
        self.ui_powerLimit_display(self.powerLimit)

    def slot_quitApp(self):
        ret = QtWidgets.QMessageBox.information(self, "Exit", "Are are your suer want to quit?",
                                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if ret == QtWidgets.QMessageBox.Ok:
            self.close()

    def slot_about(self):
        self.ui_about = About_us.AboutUsDialog()
        self.ui_about.exec_()

    def slot_reLinkDevice(self):
        self.weightMontr_thread.stop()
        "Qt设置鼠标等待状态与恢复"
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        time.sleep(2)
        self.weightMontr_thread.render(self.port_linkType, self.plc_rs485_port, self.plc_tcp_port,
                                       self.plc_rack, self.plc_slot)
        time.sleep(0.5)
        QtWidgets.QApplication.restoreOverrideCursor()


    def slot_portSetting(self):
        self.ui_portCfg = portCfg.c_portParametersCfg()
        self.ui_portCfg.slot_writeParaDict(self.config_setting)
        self.ui_portCfg.exec_()

        if self.ui_portCfg.bool_ok:
            self.port_linkType = self.ui_portCfg.paraDict.get("Default").get("Link Type", "TCP")
            if self.port_linkType == "TCP":
                self.plc_tcp_port = self.ui_portCfg.paraDict.get("Tcp Port").get("IP address", "192.168.10.20")
                self.plc_rack = self.ui_portCfg.paraDict.get("Tcp Port").get("rack", 0)
                self.plc_slot = self.ui_portCfg.paraDict.get("Tcp Port").get("slot", 1)
            else:
                self.plc_rs485_port["COM_Port"] = self.ui_portCfg.paraDict.get("RS485 Port").get("COM_Port", "COM6")
                self.plc_rs485_port["address"] = self.ui_portCfg.paraDict.get("RS485 Port").get("address", 1)
                self.plc_rs485_port["baudrate"] = self.ui_portCfg.paraDict.get("RS485 Port").get("baudrate", 115200)
                self.plc_rs485_port["databits"] = self.ui_portCfg.paraDict.get("RS485 Port").get("databits", 8)
                self.plc_rs485_port["parity"] = self.ui_portCfg.paraDict.get("RS485 Port").get("parity", "N")
                self.plc_rs485_port["stopbits"] = self.ui_portCfg.paraDict.get("RS485 Port").get("stopbits", 1)

            self.slot_reLinkDevice()

    def slot_Query(self):
        self.queryWin = queryWin.c_dataQuery()
        self.queryWin.exec_()

    def slot_countClear(self):
        self.total_value = 0
        self.addLiquid_value = 0
        self.qualified_value = 0
        self.lineEd_total.clear()
        self.lineEd_addLiquid.clear()
        self.lineEd_qualified.clear()
        self.lineEd_unqualified.clear()
        self.lineEd_qualifiedRate.clear()

    def slot_U16convertI16(self, u16):
        if u16 >= 0x8000:
            u16 -= 0x10000
        return u16

    "the other working thread"
    def showWarnMsgbox(self, title, message, type):
        if 'Warning' == type:
            QtWidgets.QMessageBox.warning(self, title, message)
        if 'Question' == type:
            QtWidgets.QMessageBox.question(self, title, message,
                                           QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if "Information" == type:
            QtWidgets.QMessageBox.information(self, title, message, QtWidgets.QMessageBox.Ok)
        if "Critical" == type:
            QtWidgets.QMessageBox.critical(self, title, message, QtWidgets.QMessageBox.Ok)


    def update_eleScaleValue(self, order:int , weight:tuple):
        if order == 1:
            self.tableWidg_exWight.setRowCount(0)
            for row in range(1):
                self.tableWidg_exWight.insertRow(row)
                for j, colnum_ele in enumerate(weight[row*10:(row+1)*10]):
                    new_item = QtWidgets.QTableWidgetItem("%.3lf" % (float(colnum_ele) / 1000))
                    self.tableWidg_exWight.setItem(row, j, new_item)
        if order == 2:
            self.tableWidg_reWight.setRowCount(0)
            for row in range(1):
                self.tableWidg_reWight.insertRow(row)
                for j, colnum_ele in enumerate(weight[row*10:(row+1)*10]):
                    new_item = QtWidgets.QTableWidgetItem("%.3lf" % (float(colnum_ele) / 1000))
                    self.tableWidg_reWight.setItem(row, j, new_item)

    def refreshVoltRes(self, barcode:str, volt:float, res:float, totalVal:int):
        currentTmStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.lineEd_date.setText(currentTmStr)
        self.lineEd_barcode.setText(barcode)
        self.lineEd_volt.setText("%.3f" % volt)
        self.lineEd_res.setText("%.3f" % res)
        self.lineEd_sum.setText(str(totalVal))


    def refreshVoltResTable(self, barcode:str, volt:float, res:float):
        currentTmStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.tableWidg_result.setRowCount(0)

        self.seriesNumber += 1
        rowElement_list = [self.seriesNumber, currentTmStr, barcode, volt, res]
        eleStr_list = []
        for i, ele in enumerate(rowElement_list):
            if 3 <= i and i <= 4:
                    eleStr_list.append("%.3f" % ele)

            else:
                eleStr_list.append(str(ele))
        self.q_csv.put(eleStr_list)

        if self.tableWid_data.rowCount() > 30000:
                self.tableWid_data.removeRow(0)
        # add a row to tableWidget
        self.tableWid_data.insertRow(self.tableWid_data.rowCount())

        for j, ele in enumerate(rowElement_list):
            if 3 <= j and j <= 4:
                new_item = QtWidgets.QTableWidgetItem("%.3f" % ele)
            # elif j == 9:
            #     if ret[i] == 1:
            #         new_item = QtWidgets.QTableWidgetItem("%.1lf" % (float(ele // 10) / 10))
            #     else:
            #         new_item = QtWidgets.QTableWidgetItem("")
            # elif j == 10:
            #     new_item = QtWidgets.QTableWidgetItem(ele)
            #
            #     if ret[i] == 1:
            #         new_item.setBackground(QtCore.Qt.cyan)
            #     elif ret[i] == 0:
            #         pass
            #     else:
            #         # if reWeight[i] - exWeight[i + 2] > upLimit:
            #         if liquidWeigh[i] > upLimit:
            #             new_item.setBackground(QtCore.Qt.yellow)
            #         # if reWeight[i] - exWeight[i + 2] < downLimit:
            #         if liquidWeigh[i] < downLimit:
            #             new_item.setBackground(QtCore.Qt.red)
            else:
                new_item = QtWidgets.QTableWidgetItem(str(ele))
            self.tableWid_data.setItem(self.tableWid_data.rowCount() - 1, j, new_item)

        if self.tableWid_data.rowCount() > 30:
            self.tableWid_data.verticalScrollBar().setValue(self.tableWid_data.rowCount() - 30)

    def refreshDataTable(self, trayNum:tuple, exWeight:tuple, reWeight:tuple, liquidWeigh:tuple,  ret:tuple, addLiquid:tuple):
        self.tableWidg_result.setRowCount(0)
        weightData = exWeight[2:] + reWeight
        for row in range(4):
            self.tableWidg_result.insertRow(row)
            for j, colnum_ele in enumerate(weightData[row * 10:(row + 1) * 10]):
                new_item = QtWidgets.QTableWidgetItem("%.2lf" % (float(colnum_ele) / 100))
                self.tableWidg_result.setItem(row, j, new_item)

        upLimit = exWeight[0]
        downLimit = exWeight[1]
        plateNum = trayNum[0]
        inOrder = trayNum[2] - 1
        currentTmStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        state_dict = {0: "合格", 1: "补液", 2: "NG"}

        for i in range(10):
            "SN, trayNum, inOrder, record, exWeight, reWeight, down, up, liuiq, state"
            self.seriesNumber += 1
            rowElement_list = [self.seriesNumber, plateNum, inOrder * 20 + i + 1, currentTmStr, exWeight[i + 2],
                               reWeight[i], downLimit, upLimit, liquidWeigh[i], addLiquid[i],
                               state_dict.get(ret[i], "NG")]

            eleStr_list = []
            for k, ele in enumerate(rowElement_list):
                if 4 <= k and k <= 8:
                    eleStr_list.append("%.2lf" % (float(self.slot_U16convertI16(ele)) / 100))
                elif k == 9:
                    if ret[i] == 1:
                        eleStr_list.append("%.1lf" % (float(ele // 10) / 10))
                    else:
                        eleStr_list.append("")
                else:
                    eleStr_list.append(str(ele))
            self.q_csv.put(eleStr_list)

            if self.tableWid_data.rowCount() > 30000:
                self.tableWid_data.removeRow(0)
            # add a row to tableWidget
            self.tableWid_data.insertRow(self.tableWid_data.rowCount())

            for j, ele in enumerate(rowElement_list):
                if 4 <= j and j <= 8:
                    new_item = QtWidgets.QTableWidgetItem("%.2lf" % (float(self.slot_U16convertI16(ele)) / 100))
                elif j == 9:
                    if ret[i] == 1:
                        new_item = QtWidgets.QTableWidgetItem("%.1lf" % (float(ele // 10) / 10))
                    else:
                        new_item = QtWidgets.QTableWidgetItem("")
                elif j == 10:
                    new_item = QtWidgets.QTableWidgetItem(ele)

                    if ret[i] == 1:
                        new_item.setBackground(QtCore.Qt.cyan)
                    elif ret[i] == 0:
                        pass
                    else:
                        # if reWeight[i] - exWeight[i + 2] > upLimit:
                        if liquidWeigh[i] > upLimit:
                            new_item.setBackground(QtCore.Qt.yellow)
                        # if reWeight[i] - exWeight[i + 2] < downLimit:
                        if liquidWeigh[i] < downLimit:
                            new_item.setBackground(QtCore.Qt.red)
                else:
                    new_item = QtWidgets.QTableWidgetItem(str(ele))
                self.tableWid_data.setItem(self.tableWid_data.rowCount() - 1, j, new_item)

            #statistics
            self.total_value += 1
            if ret[i] <= 1:
                self.qualified_value += 1
            if ret[i] == 1:
                self.addLiquid_value += 1

        self.lineEd_total.setText(str(self.total_value))
        self.lineEd_qualified.setText(str(self.qualified_value))
        self.lineEd_addLiquid.setText(str(self.addLiquid_value))
        self.lineEd_unqualified.setText(str(self.total_value - self.qualified_value))
        if self.total_value > 0:
            qualifiedRate = float(self.qualified_value) / float(self.total_value) * 100
        else:
            qualifiedRate = 0
        self.lineEd_qualifiedRate.setText(("%.2lf" % qualifiedRate) + " %")
        if self.tableWid_data.rowCount() > 30:
            self.tableWid_data.verticalScrollBar().setValue(self.tableWid_data.rowCount() - 30)


    def refreshDataTable_2nd(self, trayNum:list, exWeight:list, reWeight:list, liquidWeigh:list,  ret:list, addLiquid:list, serNum:list):
        self.tableWidg_result.setRowCount(0)
        weightData = exWeight + reWeight
        # for row in range(4):
        #     self.tableWidg_result.insertRow(row)
        #     for j, colnum_ele in enumerate(weightData[row * 10:(row + 1) * 10]):
        #         new_item = QtWidgets.QTableWidgetItem("%.3lf" % (float(colnum_ele) / 1000))
        #         self.tableWidg_result.setItem(row, j, new_item)

        upLimit = trayNum[2]
        downLimit = trayNum[1]
        plateNum = trayNum[0]
        # inOrder = trayNum[2] - 1
        currentTmStr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        state_dict = {0: " ", 1: "OK", 2: "NG"}

        for i in range(10):
            "SN, trayNum, inOrder, record, exWeight, reWeight, down, up, liuiq, state"
            self.seriesNumber += 1
            rowElement_list = [self.seriesNumber, plateNum, serNum[i], currentTmStr, exWeight[i],
                               reWeight[i], downLimit, upLimit, liquidWeigh[i], addLiquid[i],
                               state_dict.get(ret[i], "NG")]

            eleStr_list = []
            for k, ele in enumerate(rowElement_list):
                if 4 <= k and k <= 8:
                    eleStr_list.append("%.3lf" % (float(ele) / 1000))
                elif k == 9:
                    if ret[i] > 1:
                        eleStr_list.append("%.3lf" % (float(ele) / 1000))
                    else:
                        eleStr_list.append("")
                else:
                    eleStr_list.append(str(ele))
            self.q_csv.put(eleStr_list)

            if self.tableWid_data.rowCount() > 30000:
                self.tableWid_data.removeRow(0)
            # add a row to tableWidget
            self.tableWid_data.insertRow(self.tableWid_data.rowCount())

            for j, ele in enumerate(rowElement_list):
                if 4 <= j and j <= 8:
                    new_item = QtWidgets.QTableWidgetItem("%.3lf" % (float(ele) / 1000))
                elif j == 9:
                    if ret[i] > 1:
                        new_item = QtWidgets.QTableWidgetItem("%.3lf" % (float(ele) / 1000))
                    else:
                        new_item = QtWidgets.QTableWidgetItem("")
                elif j == 10:
                    new_item = QtWidgets.QTableWidgetItem(ele)

                    if ret[i] == 1:
                        new_item.setBackground(QtCore.Qt.cyan)
                    elif ret[i] == 0:
                        pass
                    else:
                        # if reWeight[i] - exWeight[i + 2] > upLimit:
                        if liquidWeigh[i] > upLimit:
                            new_item.setBackground(QtCore.Qt.yellow)
                        # if reWeight[i] - exWeight[i + 2] < downLimit:
                        if liquidWeigh[i] < downLimit:
                            new_item.setBackground(QtCore.Qt.red)
                else:
                    new_item = QtWidgets.QTableWidgetItem(str(ele))
                self.tableWid_data.setItem(self.tableWid_data.rowCount() - 1, j, new_item)

            #statistics
            self.total_value += 1
            if ret[i] <= 1:
                self.qualified_value += 1
            if ret[i] == 1:
                self.addLiquid_value += 1

        self.lineEd_total.setText(str(self.total_value))
        self.lineEd_qualified.setText(str(self.qualified_value))
        self.lineEd_addLiquid.setText(str(self.addLiquid_value))
        self.lineEd_unqualified.setText(str(self.total_value - self.qualified_value))
        if self.total_value > 0:
            qualifiedRate = float(self.qualified_value) / float(self.total_value) * 100
        else:
            qualifiedRate = 0
        self.lineEd_qualifiedRate.setText(("%.2lf" % qualifiedRate) + " %")
        if self.tableWid_data.rowCount() > 20:
            # self.tableWid_data.verticalScrollBar().setValue(self.tableWid_data.rowCount()-10)
            self.tableWid_data.scrollToBottom()

    def slot_updateDataStatistics(self):
        self.lineEd_total.setText(str(self.total_value))
        self.lineEd_qualified.setText(str(self.qualified_value))
        self.lineEd_addLiquid.setText(str(self.addLiquid_value))
        self.lineEd_unqualified.setText(str(self.total_value - self.qualified_value))
        if self.total_value > 0:
            qualifiedRate = float(self.qualified_value) / float(self.total_value) * 100
        else:
            qualifiedRate = 0
        self.lineEd_qualifiedRate.setText(("%.2lf" % qualifiedRate) + " %")

    def closeEvent(self, event):
        # stop run the program
        # defaultparaDict = {
        #     "RS485 Port": {"COM_Port": "COM3", "address": 1, "baudrate": 19200, "databits": 8, "parity": 'N',
        #                  "stopbits": 1},
        #     "Tcp Port": {"IP address": "192.168.1.1", "address": 1},
        #     "Default": {"Link Type": "TCP", "Total count": 0, "Qualified count": 0, "AddLiquid count": 0}
        # }
        defaultparaDict = {
            "RS485 Port": {"COM_Port": "COM3", "address": 1, "baudrate": 19200, "databits": 8, "parity": 'N',
                           "stopbits": 1},
            "Tcp Port": {"IP address": "192.168.10.20", "rack": 0, "slot": 1},
            "Default": {"Link Type": "TCP"}
        }
        if self.port_linkType:
            defaultparaDict["Default"]["Link Type"] = self.port_linkType
        defaultparaDict["Tcp Port"]["IP address"] = self.plc_tcp_port
        defaultparaDict["Tcp Port"]["rack"] = self.plc_rack
        defaultparaDict["Tcp Port"]["slot"] = self.plc_slot
        # defaultparaDict["Default"]["Total count"] = self.total_value
        # defaultparaDict["Default"]["Qualified count"] = self.qualified_value
        # defaultparaDict["Default"]["AddLiquid count"] = self.addLiquid_value
        subCd.saveConfig(defaultparaDict, self.plc_rs485_port)

        self.weightMontr_thread.stop()
        sys.exit()






class c_mointerThread(QtCore.QThread):
    mointer_msgBox = QtCore.pyqtSignal(str, str, str)
    # int: 1. fore , 2. re ; tuple : weight value
    mointer_weightRead = QtCore.pyqtSignal(int, tuple)
    # 1. tuple : foreWeight ; 2. tuple : reWeight
    mointer_wghRetRead = QtCore.pyqtSignal(tuple, tuple)
    # 1. tuple : tray number ; 2. tuple : foreWeight(down, up) ; 3. tuple : reWeight ; 4 tuple : liquid Weigh   5. tuple : result state ; 6. tuple : addLiquid
    mointer_weighingInfo = QtCore.pyqtSignal(tuple, tuple, tuple, tuple, tuple, tuple)
    # trayNumer(down, up), foreWeigh, reWeight, liquid Weight, result, addLiquid, SerialNum
    mointer_wghInfo = QtCore.pyqtSignal(list, list, list, list, list, list, list)

    # barcode , voltage , resistance , total sum
    mointer_S7Info = QtCore.pyqtSignal(str, float, float, int)
    #
    mointer_S7record = QtCore.pyqtSignal(str, float, float)

    def __init__(self, parent=None):
        super(c_mointerThread, self).__init__(parent)

        self.lastTIme = time.time()
        self.linkType = ""
        self.port_tcp = ""
        self.plc_rack = 0
        self.plc_slot = 1
        self.port_RS485 = {}
        self.inAddress = 0x01
        # inside state
        self._run_state = False
        self._lastTime = time.time()
        self._weighRefresh_gab = 0.5

    def render(self, linkType, rs485_dict, tcp_addr, rack=0, slot=0x01):
        self.linkType = "TCP"
        self.port_RS485 = rs485_dict
        self.port_tcp = tcp_addr
        self.plc_rack = rack
        self.plc_slot = slot
        self._run_state = True
        self.start()

    def stop(self):
        self._run_state = False

    def run(self):
        try :
            " initial the port and "
            time.sleep(2)

            # mHost = modbus_tcp.TcpMaster(host="192.168.10.11")
            # mHost.set_timeout(8.0)
            # query = mHost.execute(0x01, tkCst.READ_HOLDING_REGISTERS, 2000, 10)
            # print(query)
            # mHost.execute(0x01, tkCst.WRITE_SINGLE_REGISTER, 1502, output_value=0x1)

            comm_gab = 0.03
            weighStartTm = time.time()
            eleScale_commGab = 0.5
            readLab_risingEdge = False
            hostPort = None

            # if self.linkType == "RS485":
            #     comPort = self.port_RS485.get("COM_Port", "COM4")
            #     baudrate = self.port_RS485.get("baudrate", 19200)
            #     dataBit = self.port_RS485.get("databits", 8)
            #     parity = self.port_RS485.get("parity", "N")
            #     stopBit = self.port_RS485.get("stopbits", 1)
            #     self.inAddress = self.port_RS485.get("address", 1)
            #
            #     hostPort = tkRtu.RtuMaster(serial.Serial(port=comPort, baudrate=baudrate, bytesize=dataBit,
            #                                                   parity=parity, stopbits=stopBit, rtscts=False))
            #     hostPort.set_verbose(True)
            #     hostPort.set_timeout(10)
            # elif self.linkType == "TCP":
            #     hostPort = modbus_tcp.TcpMaster(host=self.port_tcp)
            #     hostPort.set_timeout(8.0)
            # else:
            #     self.mointer_msgBox.emit("Link Err", self.tr("端口链接类型设置错误， 请检查！\n"), "Warning")
            #     return

            if self.linkType == "TCP":
                hostPort = snap7.client.Client(lib_location="./snap7.dll")
                hostPort.connect(self.port_tcp, self.plc_rack, self.plc_slot)
            else:
                self.mointer_msgBox.emit("Link Err", self.tr("端口链接类型设置错误， 请检查！\n"), "Warning")
                return

            while self._run_state:
                currentTm = time.time()
                if currentTm - self._lastTime > comm_gab:
                    # hostPort.execute(self.inAddress, tkCst.WRITE_SINGLE_REGISTER, 1502, output_value=0x01)
                    # always write
                    # hostPort.execute(self.inAddress, tkCst.WRITE_SINGLE_REGISTER, 502, output_value=0x01)

                    # query plc ready state
                    # activity_D1500 = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 500, 2)
                    # DB number 2,  address 1798
                    activity_D1500 = hostPort.read_area(snap7.types.Areas.DB, 2, 1798, 1)
                    if activity_D1500[0] & 0x04 == 0x04:
                        if readLab_risingEdge == False:
                            # # trayNumber = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 1510, 4)
                            # # fore_weight = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 1598, 22)
                            # # re_weight = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 1650, 20)
                            # # liquidWgh = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 1700, 20)
                            # # result = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 1750, 20)
                            # # addLiquid = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 1800, 20)
                            # # self.mointer_wghRetRead.emit(fore_weight[2:], re_weight)
                            #
                            # trayNumber = []
                            # fore_weight = []
                            # re_weight = []
                            # liquidWgh = []
                            # result = []
                            # addLiquid = []
                            # serNum = []
                            # trayNum_tup = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 300, 20)
                            # trayNumber.append(subCd.U16_convertDI32(trayNum_tup[10], trayNum_tup[11]))
                            # trayNumber.append(subCd.U16_convertDI32(trayNum_tup[2], trayNum_tup[3]))
                            # trayNumber.append(subCd.U16_convertDI32(trayNum_tup[0], trayNum_tup[1]))
                            # queryInfo = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 100, 120)
                            # for i in range(0, 10):
                            #     fore_weight.append(subCd.U16_convertDI32(queryInfo[i*2], queryInfo[i*2 + 1]))
                            #     re_weight.append(subCd.U16_convertDI32(queryInfo[i*2 + 20], queryInfo[i*2 + 21]))
                            #     liquidWgh.append(subCd.U16_convertDI32(queryInfo[i*2 + 40], queryInfo[i*2 + 41]))
                            #     addLiquid.append(subCd.U16_convertDI32(queryInfo[i*2 + 60], queryInfo[i*2 + 61]))
                            #     result.append(subCd.U16_convertDI32(queryInfo[i*2 + 80], queryInfo[i*2 + 81]))
                            #     serNum.append(subCd.U16_convertDI32(queryInfo[i*2 + 100], queryInfo[i*2 + 101]))
                            #
                            # # send all result to UI plane
                            # # self.mointer_weighingInfo.emit(trayNumber, fore_weight, re_weight, liquidWgh, result, addLiquid)
                            #
                            # self.mointer_wghInfo.emit(trayNumber, fore_weight, re_weight, liquidWgh, result, addLiquid, serNum)
                            # # change the finish label
                            # # hostPort.execute(self.inAddress, tkCst.WRITE_SINGLE_REGISTER, 1504, output_value=0x01)
                            # hostPort.execute(self.inAddress, tkCst.WRITE_SINGLE_REGISTER, 500, output_value=0x00)


                            barBuffer = hostPort.read_area(snap7.types.Areas.DB, 2, 1800, 80)
                            barcode = struct.unpack_from('>60s', barBuffer, 2)
                            barcodeS = bytes.decode(barcode[0].strip(b'\x00'), encoding="utf-8")

                            voltBuffer = hostPort.read_area(snap7.types.Areas.DB, 2, 384, 8)
                            voltRes = struct.unpack('>2f', voltBuffer)

                            self.mointer_S7record.emit(barcodeS.strip(), voltRes[0], voltRes[1])

                            wValue = struct.pack('>i', (activity_D1500[0] | 0x08))
                            hostPort.write_area(snap7.types.Areas.DB, 2, 1798, wValue[0:1])

                            readLab_risingEdge = True
                    else:
                        readLab_risingEdge = False
                    self._lastTime = time.time()
                if currentTm - weighStartTm > eleScale_commGab:
                    # read fore electronic balance       foreWeight : 1
                    # exWeight = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 400, 20)
                    # ex_Wgh = []
                    # for j in range(0, 10):
                    #     ex_Wgh.append(subCd.U16_convertDI32(exWeight[j*2], exWeight[j*2 + 1]))
                    # self.mointer_weightRead.emit(1, tuple(ex_Wgh))
                    #
                    # # read re electronic balance
                    # reWeight = hostPort.execute(self.inAddress, tkCst.READ_HOLDING_REGISTERS, 420, 20)
                    # re_Wgh = []
                    # for j in range(0, 10):
                    #     re_Wgh.append(subCd.U16_convertDI32(reWeight[j*2], reWeight[j*2 + 1]))
                    # self.mointer_weightRead.emit(2, tuple(re_Wgh))

                    barBuffer = hostPort.read_area(snap7.types.Areas.DB, 2, 1800, 80)
                    barcode = struct.unpack_from('>60s', barBuffer, 2)
                    barcodeS = bytes.decode(barcode[0].strip(b'\x00'), encoding="utf-8")

                    voltBuffer = hostPort.read_area(snap7.types.Areas.DB, 2, 384, 8)
                    voltRes = struct.unpack('>2f', voltBuffer)

                    sumBuffer = hostPort.read_area(snap7.types.Areas.DB, 7, 1534, 4)
                    totalVal = struct.unpack('>l', sumBuffer)
                    weighStartTm = time.time()
                    print(barcode[0].strip(b'\x00'), voltRes[0], voltRes[1], totalVal[0])
                    self.mointer_S7Info.emit(barcodeS.strip(), voltRes[0], voltRes[1], totalVal[0])
            hostPort.disconnect()
        except Exception as err:
            self.mointer_msgBox.emit("Error", "Run time error, Please check!\n" + str(err), "Critical")








class c_dataSavemointerThread(QtCore.QThread):
    dataThread_msgBox = QtCore.pyqtSignal(str, str, str)
    def __init__(self, parent=None):
        super(c_dataSavemointerThread, self).__init__(parent)
        "Create a new floder"
        # parentDir = os.path.split(os.getcwd())[0]
        parentDir = os.getcwd()
        if not os.path.isdir(os.path.join(parentDir, 'data')):
            os.mkdir(os.path.join(parentDir, 'data'))
        self.parentDir = os.path.join(parentDir, 'data')
        self.csv_q = None

        self.ID = 0

    def render(self, queue):
        self.csv_q = queue
        self.start()

    def run(self):
        filename_s = time.strftime("%Y-%m-%d") + ".csv"
        if not os.path.exists(os.path.join(self.parentDir, filename_s)):
            with open(os.path.join(self.parentDir, filename_s), "a+", newline='') as csv_handle:
                writer = csv.writer(csv_handle)
                # writer.writerow(["序号", "料盘号", "托盘中编号", "记录时间", "前称重", "后称重", "下限", "上限", "注液量", "补液量", "状态"])
                writer.writerow(["序号", "时间日期", "条码", "电压", "内阻"])

        batteryInfo_conn = sqlite3.connect(".\\batteryData.db")
        batteryInfo_db = batteryInfo_conn.cursor()
        # batteryInfo_db.execute("""create table if not exists weight_tab (ID INT PRIMARY KEY, trayNum INT,
        #                         insideNum INT, dateTime CHAR(20), exWight FLOAT, reWight FLOAT , limitDown FLOAT ,
        #                         limitUp FLOAT , injVolume FLOAT , reVolume FLOAT, state CHAR(10))""")
        batteryInfo_db.execute("""create table if not exists weight_tab (ID INT PRIMARY KEY, dateTime CHAR(20),
                                  barcode CHAR(60), volt FLOAT, resis FLOAT )""")

        batteryInfo_db.execute("SELECT max(rowid) from weight_tab")
        n = batteryInfo_db.fetchone()[0]
        if n:
            self.ID = n
        while True:
            if not self.csv_q.empty():
                with open(os.path.join(self.parentDir, filename_s), "a+", newline='') as csv_handle:
                    while (not self.csv_q.empty()):
                        acquire_value = self.csv_q.get()
                        writer = csv.writer(csv_handle)
                        writer.writerow(acquire_value)
                        # if acquire_value[9]:
                        #     addLiquid = float(acquire_value[9])
                        # else:
                        #     addLiquid = None
                        self.ID += 1
                        # batteryInfo_db.execute("INSERT INTO weight_tab (ID, trayNum, insideNum, dateTime, exWight, reWight, limitDown, limitUp, injVolume, reVolume, state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.ID, int(acquire_value[1]), int(acquire_value[2]), acquire_value[3],
                        #            float(acquire_value[4]), float(acquire_value[5]), float(acquire_value[6]),
                        #            float(acquire_value[7]), float(acquire_value[8]), addLiquid, acquire_value[10]))
                        batteryInfo_db.execute("INSERT INTO weight_tab (ID, dateTime, barcode, volt, resis) VALUES (?, ?, ?, ?, ?)", (self.ID, acquire_value[1],
                                   acquire_value[2], float(acquire_value[3]), float(acquire_value[4])))
                        time.sleep(0.009)
                batteryInfo_conn.commit()
            time.sleep(0.005)

        batteryInfo_conn.commit()
        batteryInfo_db.close()
        batteryInfo_conn.close()





if __name__ == '__main__':
    import image_rc
    import verify_usbK

    startCase = False
    try:
        keyState = verify_usbK.check_usbKeyState()
        startCase = True

        for i, state in enumerate(keyState):
            if state == False:
                startCase = False
                break
    except Exception as err:
        pass
    startCase = True
    app = QtWidgets.QApplication(sys.argv)
    if startCase == False:
        " Do not find the usb Dongle "
        err_Msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Error", "Not authorized! Please try it again!")
        err_Msg.show()
    else:
        splash = QtWidgets.QSplashScreen(QtGui.QPixmap(""))
        splash.show()
        app.processEvents()
        time.sleep(0.8)
        Ui_Win = c_weighMointor()
        Ui_Win.show()
        splash.finish(Ui_Win)
    sys.exit(app.exec_())

    # app = QtWidgets.QApplication(sys.argv)
    # splash = QtWidgets.QSplashScreen(QtGui.QPixmap("./icon/logo_InitialStart.png"))
    # splash.show()
    # app.processEvents()
    # time.sleep(0.8)
    # Ui_Win = c_weighMointor()
    # Ui_Win.show()
    # splash.finish(Ui_Win)
    # sys.exit(app.exec_())

    # mHost = modbus_tcp.TcpMaster(host="192.168.10.11")
    # mHost.set_timeout(8.0)
    # query = mHost.execute(0x01, tkCst.READ_HOLDING_REGISTERS, 2000, 10)
    # print(query)
    # mHost.execute(0x01, tkCst.WRITE_SINGLE_REGISTER, 1502, output_value=0x1)