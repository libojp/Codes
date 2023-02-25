#!/usr/bin/python3
#-*- coding: utf-8 -*-


from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import sys
import datetime
import loginPanel_Des
from LoginPanel_PasswordM import *
import sqlite3





class login_M(QDialog, loginPanel_Des.Ui_Form):
    def __init__(self, parent=None):
        super(login_M, self).__init__(parent) ;
        self.setupUi(self) ;
        self.setWindowTitle(self.tr('login')) ;

        self.lineEdit_2.setEchoMode(QLineEdit.Password)
        self.powerLmt = -1 ;
        self.setAttribute(Qt.WA_TranslucentBackground) ;
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog) ;

        self.dbName = 'UserInfo.db'
        self.loginThread = ThreadWorkLogin(self.dbName) ;

        # self.connect(self.pushButton_2, SIGNAL("clicked()"), qApp, SLOT('close()')) ;
        self.pushButton_2.clicked.connect(self.close)
        self.pushButton.clicked.connect(self.userLoginEvent) ;
        # self.connect(self.loginThread, SIGNAL("WightValueOut(int)"), self.wigthEventOut) ;
        self.loginThread.weightOut.connect(self.wigthEventOut)

    def userLoginEvent(self):
        # self.window().hide() ;
        # PW_Manger = QDialog() ;
        # ui = Ui_Form() ;
        # ui.setupUi(PW_Manger) ;
        # PW_Manger.show() ;
        # PW_Manger.exec_() ;
        # self.window().show() ;
        # pass ;
        username = str(self.lineEdit.text()) ;
        password = str(self.lineEdit_2.text()) ;
        if username and password :
            self.loginThread.render(username, password) ;
        else:
            QMessageBox.critical(self, 'Warning', "The username or password can't be empty!") ;
        self.lineEdit.setText(self.tr(""))
        self.lineEdit_2.setText(self.tr(""))

    def wigthEventOut(self, wight):
        self.powerLmt = wight ;
        if self.powerLmt <= 0 :
            QMessageBox.critical(self, "Warning", "The user don't exist or password was wrong!") ;
        elif self.powerLmt >= 4:
            self.window().hide() ;
            # PowerWeight = QWidget() ;
            # ui = AboutUsDialog(PowerWeight) ;
            # # ui.setupUi(PowerWeight) ;
            # ui.show()
            # ui.exec_() ;
            # self.close() ;
            '''///////////////////////////////////////////////////////////////////////'''
            # P = QDialog() ;
            # ui = PasswordManger(self.dbName) ;
            # ui.setupUi(P);
            # P.show() ;
            # P.exec_() ;
            self.managerWin = PasswordManger(self.dbName) ;
            self.managerWin.show() ;
            self.managerWin.exec_()
            self.window().close()

        else:
            self.close() ;

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            QApplication.postEvent(self, QEvent(174))
            event.accept()

    def mouseMoveEvent(self, event):

        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()






class ThreadWorkLogin(QThread):
    weightOut = pyqtSignal(int)

    def __init__(self, dbPath):
        super(ThreadWorkLogin, self).__init__() ;
        self.dbPath = dbPath ;
        self.initDB()
        self.user = '' ;
        self.pwd = '' ;

    def initDB(self):
        if os.path.exists(self.dbPath):
            self.conn = sqlite3.connect(self.dbPath) ;
            self.cursor = self.conn.cursor();
        else:
            self.conn = sqlite3.connect(self.dbPath) ;
            self.cursor = self.conn.cursor();
            self.conn.execute("""CREATE TABLE INFO (ID int PRIMARY KEY NOT NULL, USERNAME char(255), PASSWORD char(255),
             AUTHORITY int, LOGINTIMES int, LASTLOGINTIME char(255) )""") ;
            # insert a default user
            self.conn.execute("INSERT INTO INFO VALUES(%d, '%s', '%s', %d, %d, '%s')" % (1, 'user', '123', 7, 0, '')) ;
        # 关闭Cursor:
        self.cursor.close() ;
        # 提交事务:
        self.conn.commit() ;
        # 关闭Connection:
        self.conn.close() ;

    def render(self, user, pwd):
        self.user = user ;
        self.pwd = pwd ;
        self.run() ;

    def run(self):
        self.conn = sqlite3.connect(self.dbPath) ;
        self.cursor = self.conn.cursor() ;
        self.cursor.execute('select * from INFO where USERNAME=? and PASSWORD=?', (self.user, self.pwd)) ;
        userResult = None ;
        userResult = self.cursor.fetchall() ;
        wight = -1 ;
        if userResult :
            wight = userResult[0][3] ;
            self.cursor.execute("UPDATE INFO SET LOGINTIMES=%d, LASTLOGINTIME='%s' WHERE USERNAME='%s'" % (userResult[0][4]+1, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.user)) ;
            self.conn.commit() ;
        # print(userResult) ;
        # self.emit(SIGNAL("WightValueOut(int)"), wight) ;
        self.weightOut.emit(wight)
        self.cursor.close() ;
        self.conn.close()




















if __name__ == '__main__':
    app = QApplication(sys.argv) ;
    FromUi = login_M() ;
    FromUi.show() ;
    sys.exit(app.exec_()) ;
