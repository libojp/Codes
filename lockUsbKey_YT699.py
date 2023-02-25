#!/usr/bin/python3
# -*- coding: utf-8 -*-


from ctypes import *


objDll = windll.LoadLibrary("Syunew3D.dll")


"""         Find Port           """
usbKeyPath = (b"" * 100)
sUkeyPath_In = c_char_p()
sUkeyPath_In.value = usbKeyPath
objDll.FindPort(0, sUkeyPath_In)
print(sUkeyPath_In.value)



"""      Set Read Parword       """
W_HKey_In = c_char_p(b'F603729F')
W_LKey_In = c_char_p(b'F603729F')
new_HKey_In = c_char_p(b'F603729F')
new_LKey_In = c_char_p(b'F603729F')
objDll.SetReadPassword(W_HKey_In, W_LKey_In, new_HKey_In, new_LKey_In, sUkeyPath_In)


"""      YWriteString     """
InStringW1 = c_char_p(b'Azazel')
objDll.YWriteString(InStringW1, 0x0, new_HKey_In, new_LKey_In, sUkeyPath_In)


"""      Get Chip ID   """
ChipIDStr = c_char_p(b'\0' * 50)
objDll.GetChipID(ChipIDStr, sUkeyPath_In)


"""      Get ID Digit   """
id1_in = c_uint32(0)
id2_in = c_uint32(0)
objDll.GetID(byref(id1_in), byref(id2_in), sUkeyPath_In)
print("%X" % id1_in.value, "%X" % id2_in.value, id1_in.value, id2_in.value)



"""      Using the YT699 encrpyte the data   """
encStrSub1 = "0A0E090A0806020708020F0B0502050C090B0106"
encStrEnd = "1234567890ABCDEFABCDEF0123456789"
encInputString = encStrSub1 + ("%X" % id1_in.value) + ("%X" % id2_in.value) + encStrEnd
encInputStrPoint = c_char_p(b'\0' * (len(encInputString) + 10))
encInputStrPoint.value = str.encode(encInputString)
encOutString = c_char_p(b'\0' * (len(encInputString) + 10))
objDll.EncString(encInputStrPoint, encOutString, sUkeyPath_In)
print(encOutString.value, len(encOutString.value))
# print encOutString.value
print(encInputStrPoint.value, len(encInputStrPoint.value))


"""     Write the Second encrpyte data    """
"""Watch out !  It's encOutString.value not encOutString"""
# ObjDll.YWriteString(encOutString ,0x20 ,new_HKey_In ,new_LKey_In ,sUkeyPath_In) ;
objDll.YWriteString(encOutString.value, 0x20, new_HKey_In, new_LKey_In, sUkeyPath_In)




objDll_SHA256 = windll.LoadLibrary('sha256.dll')
"""     calc the digest out value   """
digestStr = b'\0' * 256
digestStrPoint = c_char_p()
digestStrPoint.value = digestStr
objDll_SHA256.sha256(encInputStrPoint, len(encInputStrPoint.value), digestStrPoint)
print(digestStrPoint.value)


char_ValOut = ( c_uint8 * 32)()
objDll_SHA256.sha256(encInputStrPoint, len(encInputStrPoint.value), char_ValOut)
for i in char_ValOut:
    print(i ,)
digoutStrLink = ""
for i in char_ValOut:
    digoutStrLink += ('%02X' % i)
print(digoutStrLink)


"""   Write the third encrypte data  """
digestStr_0x = c_char_p(b'\0' * (len(digoutStrLink) + 10))
digestStr_0x.value = str.encode(digoutStrLink)
objDll.YWriteString(digestStr_0x.value, 0x120, new_HKey_In, new_LKey_In, sUkeyPath_In)