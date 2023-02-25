# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PWD Manger.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QPushButton, QTableWidget, QAbstractItemView



# try:
#     _fromUtf8 = QtCore.QString.fromUtf8
# except AttributeError:
#     def _fromUtf8(s):
#         return s
#
# try:
#     _encoding = QApplication.UnicodeUTF8
#     def _translate(context, text, disambig):
#         return QApplication.translate(context, text, disambig, _encoding)
# except AttributeError:
#     def _translate(context, text, disambig):
#         return QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(("Form"))
        Form.resize(791, 271)
        Form.setMaximumSize(QtCore.QSize(791, 271))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap((":/icon/Icon/508422.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        # Form.setWindowFlags(QtCore.Qt.FramelessWindowHint|QtCore.Qt.Dialog)
        self.tableWidget = QTableWidget(Form)
        self.tableWidget.setGeometry(QtCore.QRect(0, 0, 701, 271))
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setObjectName(("tableWidget"))
        self.tableWidget.horizontalHeader().setCascadingSectionResizes(False)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(100)
        self.tableWidget.horizontalHeader().setSortIndicatorShown(False)
        columm_width = [90, 185, 100, 100, 220];
        for colnum in range(5):
            self.tableWidget.setColumnWidth(colnum, columm_width[colnum]);
        headerlabels = ['UserName', 'Password', 'Authority', 'LoginTimes', 'Last Login Time'];
        self.tableWidget.setHorizontalHeaderLabels(headerlabels);
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers);
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows);
        self.AddUserButton = QPushButton(Form)
        self.AddUserButton.setGeometry(QtCore.QRect(700, 0, 91, 31))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap((":/icon/Icon/add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.AddUserButton.setIcon(icon1)
        self.AddUserButton.setObjectName(("AddUserButton"))
        self.EditUserButton = QPushButton(Form)
        self.EditUserButton.setGeometry(QtCore.QRect(700, 30, 91, 31))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap((":/icon/Icon/edit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.EditUserButton.setIcon(icon2)
        self.EditUserButton.setObjectName(("EditUserButton"))
        self.DelUserButton = QPushButton(Form)
        self.DelUserButton.setGeometry(QtCore.QRect(700, 60, 91, 31))
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap((":/icon/Icon/del.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.DelUserButton.setIcon(icon3)
        self.DelUserButton.setObjectName(("DelUserButton"))
        self.QuitButton = QPushButton(Form)
        self.QuitButton.setGeometry(QtCore.QRect(700, 240, 91, 31))
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap((":/icon/Icon/1506.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.QuitButton.setIcon(icon4)
        self.QuitButton.setObjectName(("QuitButton"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "PWD Manger", None))
        self.AddUserButton.setText(_translate("Form", "Add User", None))
        self.EditUserButton.setText(_translate("Form", "Edit User", None))
        self.DelUserButton.setText(_translate("Form", "Dele User", None))
        self.QuitButton.setText(_translate("Form", "Quit App", None))


import image_rc

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

