#!/usr/bin/python3
#-*- coding: utf-8 -*-


import sys
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QMessageBox, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtWidgets import QLineEdit, QPushButton, QGroupBox, QComboBox
from PyQt5.QtCore import *
from PyQt5.QtGui import QIntValidator
import datetime
import sqlite3
import MangerUi



weightValue = {'Opertor': 1, 'Engineer': 2, 'Senior Engineer': 3, 'Manager': 4, 'Administrators': 5} ;
combox_listName = ['Normal User', 'Opertor', 'Engineer', 'Senior Engineer', 'Manager', 'Administrators'] ;


class PasswordManger(QDialog, MangerUi.Ui_Form):
    def __init__(self, dbPath, parent=None):
        super(PasswordManger, self).__init__(parent) ;
        self.setupUi(self) ;

        self.dbPath = dbPath ;
        self.initConnectDB() ;
        self.setWindowFlags(Qt.WindowCloseButtonHint) ;
        self.AddUserButton.clicked.connect(self.newAction_addUser) ;
        self.EditUserButton.clicked.connect(self.editAction_editUser) ;
        self.DelUserButton.clicked.connect(self.delAction_delUser) ;
        # self.QuitButton.clicked.connect(QCoreApplication.quit) ;
        self.QuitButton.clicked.connect(self.close);

    def initConnectDB(self):
        self.conn = sqlite3.connect(self.dbPath) ;
        self.cursor = self.conn.cursor() ;
        self.cursor.execute("SELECT * FROM INFO") ;
        self.displayData = self.cursor.fetchall() ;
        self.current_row = len(self.displayData) ;
        # print(self.displayData)
        for row in range(self.current_row):
            self.tableWidget.insertRow(self.displayData[row][0] - 1) ;
            for i in range(5):
                if i == 2:
                    new_item = QTableWidgetItem(combox_listName[self.displayData[row][i+1]]) ;
                elif i == 3:
                    # new_item = QTableWidgetItem(QString("%1").arg(self.displayData[row][i+1]))
                    new_item = QTableWidgetItem(("%d") % (self.displayData[row][i + 1]))
                else:
                    new_item = QTableWidgetItem(self.displayData[row][i+1]) ;
                self.tableWidget.setItem(self.displayData[row][0] - 1, i, new_item) ;

    def getDB_UpdateData(self):
        self.cursor.execute("SELECT * FROM INFO") ;
        self.displayData = self.cursor.fetchall() ;
        self.current_row = len(self.displayData) ;

    def newAction_addUser(self):
        dialogResult = self.showDialog() ;
        if dialogResult[0]:
            if dialogResult[1] and dialogResult[2] :
                userNames = [x[1] for x in self.displayData] ;
                if not ( dialogResult[1] in userNames ):
                    self.current_row += 1 ;
                    self.tableWidget.insertRow(self.current_row - 1) ;
                    for i in range(5):
                        if i == 2:
                            new_item = QTableWidgetItem(combox_listName[dialogResult[i+1]]) ;
                        elif i == 3:
                            # new_item = QTableWidgetItem(QString("%1").arg(dialogResult[i+1])) ;
                            new_item = QTableWidgetItem("%d" % (dialogResult[i + 1]))
                        else:
                            new_item = QTableWidgetItem(dialogResult[i+1]) ;
                        self.tableWidget.setItem(self.current_row - 1, i, new_item) ;
                    # Save new item to database
                    self.cursor.execute("INSERT INTO INFO VALUES(%d, '%s', '%s', %d, %d, '%s')" %
                                        (self.current_row, dialogResult[1], dialogResult[2], dialogResult[3], dialogResult[4], dialogResult[5])) ;
                    self.conn.commit() ;
                    # Update DB table data to variable self.displayData
                    self.getDB_UpdateData() ;
                else:
                    QMessageBox.critical(self, "Warning", "The user name was exist!") ;
            else:
                QMessageBox.critical(self, "Warning", "The UserName or Password can't be empty!") ;

    def editAction_editUser(self):
        selected_row = self.tableWidget.selectedItems() ;
        if selected_row:
            edit_row = self.tableWidget.row(selected_row[0]) ;
            old_data = [] ;
            for i in range(5):
                if i == 2 :
                    old_data.append(weightValue[str(self.tableWidget.item(edit_row, i).text())]) ;
                elif i == 3:
                    old_data.append(int(self.tableWidget.item(edit_row, i).text()))
                else:
                    old_data.append(self.tableWidget.item(edit_row, i).text()) ;
            new_data = self.showDialog(*old_data) ;
            if new_data[0]:
                if new_data[1] and new_data[2]:
                    userNames = [x[1] for x in self.displayData] ;
                    #  user name maybe already exist
                    if userNames.count(new_data[1]) <= 1 :
                        for i in range(5):
                            if i == 2:
                                new_item = QTableWidgetItem(combox_listName[new_data[i+1]]) ;
                            elif i == 3:
                                new_item = QTableWidgetItem("%1" % (new_data[i+1])) ;
                            else:
                                new_item = QTableWidgetItem(new_data[i+1]) ;
                            self.tableWidget.setItem(edit_row, i, new_item) ;
                        self.cursor.execute("""UPDATE INFO SET USERNAME = '%s', PASSWORD = '%s', AUTHORITY = %d, 
                        LOGINTIMES = %d, LASTLOGINTIME='%s' WHERE ID = %d""" % (new_data[1], new_data[2], new_data[3],
                                                                                new_data[4], new_data[5], edit_row + 1)) ;
                        self.conn.commit() ;
                        # Update DB table data to variable self.displayData
                        self.getDB_UpdateData() ;
                    else:
                        QMessageBox.critical(self, "Warning", "The user name was exist!");
                else:
                    QMessageBox.critical(self, "Warning", "The UserName or Password can't be empty!");
        else:
            self.showHint()

    def delAction_delUser(self):
        selected_row = self.tableWidget.selectedItems() ;
        if selected_row:
            del_row = self.tableWidget.row(selected_row[0]) ;
            self.cursor.execute('DELETE FROM INFO WHERE ID = %d' % (del_row + 1)) ;
            self.tableWidget.removeRow(del_row) ;
            for index in range(del_row + 2, self.current_row + 1):
                self.cursor.execute('UPDATE INFO SET ID=%d WHERE ID=%d' % ((index - 1), index)) ;
            self.conn.commit() ;
            self.current_row -= 1 ;
            # Update DB table data to variable self.displayData
            self.getDB_UpdateData() ;
        else:
            self.showHint() ;

    def showDialog(self, un='', pw='', wg=1, times=0, timeT=''):
        edit_dialog = QDialog(self) ;
        group = QGroupBox('Edit Info', edit_dialog) ;

        lbl_username = QLabel('Username:', group) ;
        le_username = QLineEdit(group) ;
        le_username.setText(un) ;

        lbl_password = QLabel('Password:', group) ;
        le_password = QLineEdit(group) ;
        le_password.setText(pw) ;
        le_password.setEchoMode(QLineEdit.Password) ;

        # weightValue = {'Opertor': 1, 'Engineer': 2, 'Senior Engineer': 3, 'Manager': 4, 'Administrators': 5} ;
        lbl_weight = QLabel('Authority:', group) ;
        combox_weight = QComboBox(group) ;
        # combox_listName = ['Opertor', 'Engineer', 'Senior Engineer', 'Manager', 'Administrators'] ;
        for i in range(5):
            combox_weight.insertItem(i, combox_listName[i+1]) ;
        combox_weight.setCurrentIndex(wg - 1) ;

        lbl_times = QLabel('Login Times:', group) ;
        le_times = QLineEdit(group) ;
        le_times.setText(str(times)) ;
        le_times.setValidator(QIntValidator(0, 10000)) ;

        lbl_time = QLabel('Last Login Time:', group) ;
        le_lastTime = QLineEdit(group) ;
        if timeT :
            le_lastTime.setText(timeT) ;
        else:
            le_lastTime.setText(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) ;

        ok_btn = QPushButton('OK', edit_dialog) ;
        cancel_btn = QPushButton('Cancel', edit_dialog) ;

        ok_btn.clicked.connect(edit_dialog.accept) ;
        ok_btn.setDefault(True) ;
        cancel_btn.clicked.connect(edit_dialog.reject) ;

        group_layout = QVBoxLayout() ;
        group_item = [lbl_username, le_username,
                      lbl_password, le_password,
                      lbl_weight, combox_weight,
                      lbl_times, le_times,
                      lbl_time, le_lastTime] ;
        for item in group_item:
            group_layout.addWidget(item) ;
        group.setLayout(group_layout) ;
        group.setFixedSize(group.sizeHint()) ;

        btn_layout = QHBoxLayout() ;
        btn_layout.addWidget(ok_btn) ;
        btn_layout.addWidget(cancel_btn) ;

        dialog_layout = QVBoxLayout() ;
        dialog_layout.addWidget(group) ;
        dialog_layout.addLayout(btn_layout) ;
        edit_dialog.setLayout(dialog_layout) ;
        edit_dialog.setFixedSize(edit_dialog.sizeHint()) ;

        if edit_dialog.exec_():
            username = le_username.text() ;
            password = le_password.text() ;
            weightText = combox_weight.currentText() ;
            weight = weightValue[str(weightText)] ;
            times = int(le_times.text()) ;
            lastTime = le_lastTime.text() ;
            return True, username, password, weight, times, lastTime
        return False, None, None, None, None, None ;

    def showHint(self):
        hint_msg = QMessageBox() ;
        hint_msg.setText("No selected row!") ;
        hint_msg.addButton(QMessageBox.Ok) ;
        hint_msg.exec_() ;

    def closeEvent(self, event):
        self.cursor.close()
        self.conn.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft() ;
            QApplication.postEvent(self, QEvent(174)) ;
            event.accept() ;

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition) ;
            event.accept() ;










if __name__ == '__main__':
    app = QApplication(sys.argv) ;
    ui = PasswordManger('UserInfo.db') ;
    ui.show() ;
    sys.exit(app.exec_()) ;