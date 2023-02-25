#!usr/bin/python3
# -*- coding: utf-8 -*-



from PyQt5 import QtCore, QtGui, QtWidgets
from PyUi_protConfig_v1 import Ui_Dialog
import Cd_subFunction as subCd


class c_portParametersCfg(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(c_portParametersCfg, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self.setFixedSize(self.width(), self.height())
        self.tabWidget.tabBar().hide()

        self.setWindowTitle("prot config")
        self.tabWidget.setCurrentIndex(0)

        self.bool_ok = False

        self.pushB_cancel.clicked.connect(self.close)
        self.pushB_ok.clicked.connect(self.slot_quitDialog)
        self.comb_Type.currentIndexChanged.connect(self.slot_updateTabWidgetPage)

        self.paraDict = {
            "RS485 Port": {"COM_Port": "COM3", "address": 1, "baudrate": 19200, "databits": 8, "parity": 'N',
                         "stopbits": 1},
            "Tcp Port": {"IP address": "192.168.1.1", "rack": 0, "slot": 1},
            "Default": {"Link Type": "TCP"}
        }


    def slot_updateTabWidgetPage(self, value):
        if value and value == 1:
            self.slot_refreshPorts()
        self.tabWidget.setCurrentIndex(value)

    def slot_refreshPorts(self):
        portList = subCd.foundAll_ComPort()
        self.portCombo.clear()
        for index_i, portString in enumerate(portList):
            self.portCombo.insertItem(index_i, self.tr(portString))

    def slot_writeParaDict(self, exParaDict):
        self.paraDict["Default"]["Link Type"] = exParaDict.get("Default").get("Link Type", "TCP")
        self.paraDict["Tcp Port"]["IP address"] = exParaDict.get("Tcp Port").get("IP address", "192.168.1.1")
        self.paraDict["Tcp Port"]["rack"] = exParaDict.get("Tcp Port").get("rack", 0)
        self.paraDict["Tcp Port"]["slot"] = exParaDict.get("Tcp Port").get("slot", 1)

        chNames = ["RS485 Port"]
        for name in chNames:
            if len(exParaDict.get(name)) > 0:
                self.paraDict[name]["COM_Port"] = exParaDict.get(name).get("COM_Port", "COM3")
                self.paraDict[name]["address"] = exParaDict.get(name).get("address", 1)
                self.paraDict[name]["baudrate"] = exParaDict.get(name).get("baudrate", 19200)
                self.paraDict[name]["databits"] = exParaDict.get(name).get("databits", 8)
                self.paraDict[name]["parity"] = exParaDict.get(name).get("parity", 'N')
                self.paraDict[name]["stopbits"] = exParaDict.get(name).get("stopbits", 1)
        self.updatePanelParameters()

    def updatePanelParameters(self):
        if self.paraDict["Default"]["Link Type"] == "TCP":
            self.tabWidget.setCurrentIndex(0)
        else:
            self.tabWidget.setCurrentIndex(1)
        self.comb_Type.setCurrentIndex(self.comb_Type.findText(self.paraDict.get("Default").get("Link Type", "TCP")))

        self.slot_refreshPorts()
        self.portCombo.setCurrentIndex(self.portCombo.findText(self.paraDict.get("RS485 Port").get("COM_Port", "COM3")))
        self.addressSpinner.setValue(self.paraDict.get("RS485 Port").get("address", 1))
        self.baudCombo.setCurrentIndex(self.baudCombo.findText(str(self.paraDict.get("RS485 Port").get("baudrate", 19200))))
        # the following code has the same function as the above code
        self.dataBitsCombo.setCurrentText(str(self.paraDict.get("RS485 Port").get("databits", 8)))
        parityDict = {"N": "None", "E": "Even", "O": "Odd", "S": "Space", "M": "Mark"}
        self.parityCombo.setCurrentText(parityDict[self.paraDict.get("RS485 Port").get("parity", "N")])
        self.stopBitsCombo.setCurrentText(str(self.paraDict.get("RS485 Port").get("stopbits", 1)))

        self.lineE_IP.setText(self.paraDict.get("Tcp Port").get("IP address", "192.168.10.11"))
        self.lineE_tcpStation.setText(str(self.paraDict.get("Tcp Port").get("rack", 0)))
        self.lineE_slot.setText(str(self.paraDict.get("Tcp Port").get("slot", 1)))

    def slot_getSettingParaDict(self):
        self.paraDict["Default"]["Link Type"] = self.comb_Type.currentText()
        if self.paraDict["Default"]["Link Type"] == "TCP":
            self.paraDict["Tcp Port"]["IP address"] = self.lineE_IP.text()
            self.paraDict["Tcp Port"]["rack"] = int(self.lineE_tcpStation.text())
            self.paraDict["Tcp Port"]["slot"] = int(self.lineE_slot.text())
        else:
            self.paraDict["RS485 Port"]["COM_Port"] = self.portCombo.currentText()
            self.paraDict["RS485 Port"]["address"] = self.addressSpinner.value()
            self.paraDict["RS485 Port"]["baudrate"] = int(self.baudCombo.currentText())
            self.paraDict["RS485 Port"]["databits"] = int(self.dataBitsCombo.currentText())
            self.paraDict["RS485 Port"]["parity"] = self.parityCombo.currentText()[:1]
            # print(self.ebalancePara.get("parity"))
            self.paraDict["RS485 Port"]["stopbits"] = int(self.stopBitsCombo.currentText())

    def slot_quitDialog(self):
        self.bool_ok = True
        self.slot_getSettingParaDict()
        self.close()


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    paraCfg = c_portParametersCfg()
    paraCfg.show()
    sys.exit(app.exec_())