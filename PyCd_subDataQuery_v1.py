# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_dataQuery_v101.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from PyUi_dataQuery_v3 import Ui_Form
import os
import csv
import sqlite3
import math

class c_dataQuery(QtWidgets.QDialog, Ui_Form):
    def __init__(self, parent=None):
        super(c_dataQuery, self).__init__(parent)

        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowMaximizeButtonHint | QtCore.Qt.WindowCloseButtonHint)
        for ctrl in [self.pushB_startTm, self.pushB_endTm, self.pushB_ept_1, self.pushB_ept_2]:
            ctrl.setVisible(False)

        self.dateTimeEd_start.setCalendarPopup(True)
        self.dateTimeEd_end.setCalendarPopup(True)
        self.dateTimeEd_start.setDateTime(QtCore.QDateTime.currentDateTime().addDays(-5))
        self.dateTimeEd_start.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.dateTimeEd_end.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dateTimeEd_end.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        self.initCheckBase()
        self.batteryInfo_conn = sqlite3.connect(".\\batteryData.db")
        self.batteryInfo_db = self.batteryInfo_conn.cursor()
        self.queryRet = None
        self.count_total = 0
        self.count_unqualified = 0
        self.pushB_query.clicked.connect(self.slot_query)
        self.pushB_export.clicked.connect(self.slot_exportCurrentData)
        self.pushB_del.clicked.connect(self.slot_deleteCurrentData)
        self.pushB_quit.clicked.connect(self.slot_quitApp)

        self.timer_tmData = QtCore.QTimer()
        self.timer_tmData.timeout.connect(self.updateDisplay)
        self.timer_tmData.start(1100)

    def initCheckBase(self):
        if not os.path.isfile(".\\batteryData.db"):
            QtWidgets.QMessageBox.warning(self, "Error", "没有找到相应的数据库文件， 请检查！", QtWidgets.QMessageBox.Ok)
            self.close()

    def slot_query(self):
        startTm = self.dateTimeEd_start.text()
        endTm = self.dateTimeEd_end.text()
        displayCount = self.spinBox_pagShowRows.value()
        sw_case = self.comboB_selCase.currentText()
        chk_case = self.checkBox_case.isChecked()
        print(sw_case, chk_case)
        self.count_unqualified = 0
        self.count_total = 0
        if startTm and endTm and (endTm > startTm):
            " Qt 设置鼠标等待状态与恢复 "
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            if chk_case:
                self.batteryInfo_db.execute("SELECT * FROM weight_tab WHERE dateTime BETWEEN ? AND ? AND state = ?", (startTm, endTm, sw_case))
            else:
                self.batteryInfo_db.execute("SELECT * FROM weight_tab WHERE dateTime BETWEEN ? AND ?", (startTm, endTm))
            self.queryRet = self.batteryInfo_db.fetchall()
            self.count_total = len(self.queryRet)
            self.tableWid_battInfo.setRowCount(0)
            if len(self.queryRet) > 0:
                # self.tableWid_battInfo.clear()
                displayRow = min(displayCount, len(self.queryRet))
                for i in range(displayRow):
                    # add a row to tableWidget
                    ele_tuple = self.queryRet[i]
                    self.tableWid_battInfo.insertRow(self.tableWid_battInfo.rowCount())
                    for j, ele in enumerate(ele_tuple):
                        if j == 9:
                            if ele:
                                new_item = QtWidgets.QTableWidgetItem(str(ele))
                            else:
                                new_item = QtWidgets.QTableWidgetItem("")
                        elif j == 10:
                            new_item = QtWidgets.QTableWidgetItem(str(ele))
                            if ele == "NG":
                                new_item.setBackground(QtCore.Qt.yellow)
                                self.count_unqualified += 1
                            if ele == "补液":
                                new_item.setBackground(QtCore.Qt.cyan)
                        else:
                            new_item = QtWidgets.QTableWidgetItem(str(ele))
                        self.tableWid_battInfo.setItem(self.tableWid_battInfo.rowCount() - 1, j, new_item)
                if displayCount < len(self.queryRet):
                    self.count_unqualified = sum(x.count("合格") for x in self.queryRet)
                pageState = self.count_total > displayCount
                self.pushB_fristPag.setEnabled(pageState)
                self.pushB_endPag.setEnabled(pageState)
                self.pushB_nextPag.setEnabled(pageState)
                self.pushB_previousPag.setEnabled(pageState)
            self.label_totalV.setText("{:d}".format(self.count_total))
            self.label_unqVal.setText("{:d}".format(self.count_unqualified))
            QtWidgets.QApplication.restoreOverrideCursor()
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "输入的时间格式不合法或是时间区间段有误， 请检查！")


    def slot_exportCurrentData(self):
        if self.count_total > 0 and self.queryRet:
            fileName, filetype = QtWidgets.QFileDialog.getSaveFileName(self, "Export", None, "CSV Files (*.csv);;All Files (*)")
            if fileName:
                with open(fileName, "a+", newline='') as csv_handle:
                    writer_h = csv.writer(csv_handle)
                    writer_h.writerow(["序号", "料盘号", "托盘中编号", "记录时间", "前称重", "后称重", "下限", "上限", "注液量", "补液量", "状态"])
                    writer_h.writerows(self.queryRet)
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "当前没有可导出的数据。", QtWidgets.QMessageBox.Ok)


    def slot_deleteCurrentData(self):
        if self.count_total > 0 and self.queryRet:
            ret = QtWidgets.QMessageBox.warning(self, "Warning", "请确认要删除当前所有数据？", QtWidgets.QMessageBox.Ok|QtWidgets.QMessageBox.Cancel)
            if ret == QtWidgets.QMessageBox.Ok:
                startTm = self.dateTimeEd_start.text()
                endTm = self.dateTimeEd_end.text()
                self.batteryInfo_db.execute("DELETE FROM weight_tab WHERE dateTime BETWEEN ? AND ?", (startTm, endTm))
                self.batteryInfo_conn.commit()
                self.tableWid_battInfo.setRowCount(0)
        else:
            QtWidgets.QMessageBox.warning(self, "Warning", "当前没有可删除的数据。", QtWidgets.QMessageBox.Ok)

    def updateDisplay(self):
        if self.count_total > self.spinBox_pagShowRows.value():
            totalPags = math.ceil(self.count_total / self.spinBox_pagShowRows.value())
            self.spinBox_pagGo.setMaximum(totalPags)

    def slot_quitApp(self):
        ret = QtWidgets.QMessageBox.information(self, "Exit", "Are are your suer want to quit?",
                                                QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        if ret == QtWidgets.QMessageBox.Ok:
            self.close()

    def closeEvent(self, event):
        if self.batteryInfo_db:
            self.batteryInfo_db.close()
            self.batteryInfo_conn.close()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = c_dataQuery()

    Form.show()
    sys.exit(app.exec_())

