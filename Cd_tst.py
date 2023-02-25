#!/usr/bin/python3
# -*- coding: utf-8 -*-



import os
import csv
import time
import struct




t = bytearray(b'\x124\x00P')
byt = struct.unpack_from('>4s', t)
print(byt, bytes.decode(byt[0].strip(b'\x00')).strip(), bytes.decode(byt[0]))

ret = bytearray(b'\xfe\x0babcd\x00\x00efghijk\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
s = struct.unpack_from('>20s', ret, 2)
tt = struct.unpack_from('>20s', ret[2:])
tt_s = bytes.decode(s[0])
soutt = bytes.decode(tt[0].strip(b'\x00'))
print(s, tt, bytes.decode(tt[0]), bytes.decode(s[0]), len(tt_s), soutt, len(soutt))

f = "ERROR"
bret = struct.pack('>5s', f.encode())
print(bret)

ret = bytearray(b'\xfe\x0bERROR\x00\x00abcdefghijk\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
s = struct.unpack_from('>20s', ret, 2)
tt = struct.unpack_from('>20s', ret[2:])
tt_s = bytes.decode(s[0])
soutt = bytes.decode(tt[0].strip(b'\x00'))
print(s, tt, bytes.decode(tt[0]), bytes.decode(s[0]), len(tt_s), len(tt_s.strip()), soutt, len(soutt), soutt.encode())



parentDir = os.getcwd()
if not os.path.isdir(os.path.join(parentDir, 'data')):
    os.mkdir(os.path.join(parentDir, 'data'))
newparentDir = os.path.join(parentDir, 'data')
print(newparentDir)


filename_s = time.strftime("%Y-%m-%d") + ".csv"
if not os.path.exists(os.path.join(newparentDir, filename_s)):
    with open(os.path.join(newparentDir, filename_s), "a+", newline='') as csv_handle:
        writer = csv.writer(csv_handle)
        # writer.writerow(["序号", "料盘号", "托盘中编号", "记录时间", "前称重", "后称重", "下限", "上限", "注液量", "补液量", "状态"])
        writer.writerow(["序号", r"时间日期", r"条码", r"电压", r"内阻"])
        # writer.writerow([r"num", r"date", r"barcod", r"volt", r"res"])