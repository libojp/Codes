#!/usr/bin/python3
# -*- coding: utf-8 -*-


import yaml
import serial.tools.list_ports
import struct


"""     Function    """
def foundAll_ComPort():
    plist = list(serial.tools.list_ports.comports())
    SerialList = []
    for item in plist:
        ItemPort = list(item)
        SerialList.append(ItemPort[0])
    return SerialList



def U16_convertDI32(eleLow, eleHigh):
    temp = struct.pack('<HH', eleLow, eleHigh)
    a = struct.unpack('<i', temp)
    return a[0]


def getGabTimeString(gabtime_f):
    if gabtime_f > 3600 * 24:
        return "%d  %02d:%02d:%02d" % (gabtime_f/3600 / 24, gabtime_f/3600 %24, (gabtime_f%3600)/60, gabtime_f%60)
    else:
        return "%02d:%02d:%02d" % (gabtime_f/3600 %24, (gabtime_f%3600)/60, gabtime_f%60)



def readConfig(config_setting, plc_port):
    portName = ["RS485 Port"]

    for name, para_dict in zip(portName, [plc_port]):
        if config_setting.get(name):
            para_dict["COM_Port"] = config_setting.get(name).get("COM_Port", "COM3")
            para_dict['baudrate'] = config_setting.get(name).get("baudrate", 9600)
            para_dict["parity"] = config_setting.get(name).get("parity", "N")
            para_dict["databits"] = config_setting.get(name).get("databits", 8)
            para_dict["stopbits"] = config_setting.get(name).get("stopbits", 1)
        if config_setting.get(name) and name == "RS485 Port":
            para_dict["address"] = config_setting.get(name).get("address", 0x01)



def saveConfig(defaultparaList, plc_port):
    portName = ["RS485 Port"]

    for name, para_list in zip(portName, [plc_port]):
        if len(para_list) > 0:
            defaultparaList[name]["COM_Port"] = para_list["COM_Port"]
            defaultparaList[name]["baudrate"] = para_list["baudrate"]
            defaultparaList[name]["parity"] = para_list["parity"]
            defaultparaList[name]["databits"] = para_list["databits"]
            defaultparaList[name]["stopbits"] = para_list["stopbits"]
        if len(para_list) > 0 and name == "RS485 Port":
            defaultparaList[name]["address"] = para_list["address"]

    with open("config.yaml", 'w') as yamlHandle:
        yaml.dump(defaultparaList, yamlHandle, default_flow_style=False)




