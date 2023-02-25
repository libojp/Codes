

from ctypes import *
import hashlib

strStart = "0A0E090A0806020708020F0B0502050C090B0106"
strEnd = "1234567890ABCDEFABCDEF0123456789"


new_HKey_In = create_string_buffer(b'', 8)
new_HKey_In.value = b'F603729F'
new_LKey_In = create_string_buffer(b'', 8)
new_LKey_In.value = b'F603729F'

#  return str type
def GetLinkSourceString(strStart, UkeyId1, UkeyId2, strEnd) -> str:
    return strStart + ("%X" % UkeyId1) + ("%X" % UkeyId2) + strEnd




# input para: b"  byte type
def GetCheckSumStr_sha256(sourceStr) -> str:
    sha256 = hashlib.sha256()
    sha256.update(sourceStr)
    char_ValOut = sha256.hexdigest()
    # digoutStrLink = "";
    # for i in char_ValOut:
    #     digoutStrLink += ('%02X' % i)
    # print digoutStrLink;
    return char_ValOut.upper()



# the source code had bug
def check_usbKeyState():
    ObjDll_Syunew = windll.LoadLibrary(".\\Syunew3D.dll")
    sUkeyPath_Str = create_string_buffer(b"", 100)
    ObjDll_Syunew.FindPort(0, sUkeyPath_Str)

    id1_in = c_uint32(0)
    id2_in = c_uint32(0)
    ObjDll_Syunew.GetID(byref(id1_in), byref(id2_in), sUkeyPath_Str)

    linkSourceString = GetLinkSourceString(strStart, id1_in.value, id2_in.value, strEnd);
    encrypteStringPoint = create_string_buffer(b"", 185)
    encrypteStringPoint.value = str.encode(linkSourceString)
    encrypteOutString = create_string_buffer(b'', 360)
    ObjDll_Syunew.EncString(encrypteStringPoint, encrypteOutString, sUkeyPath_Str)
    encrypteOutStr_SHA256 = GetCheckSumStr_sha256(linkSourceString.encode())

    targetAreaStr1 = create_string_buffer(b'',  20)
    ObjDll_Syunew.YReadString(targetAreaStr1, 0x0, 20, new_HKey_In, new_LKey_In, sUkeyPath_Str)

    targetAreaStr2 = create_string_buffer(b'',  200)
    ObjDll_Syunew.YReadString(targetAreaStr2, 0x20, 200, new_HKey_In, new_LKey_In, sUkeyPath_Str)

    targetAreaStr3 = create_string_buffer(b'', 201)
    ObjDll_Syunew.YReadString(targetAreaStr3, 0x120, 200, new_HKey_In, new_LKey_In, sUkeyPath_Str)

    case1 = False
    case2 = False
    case3 = False

    if len(targetAreaStr1.value) and targetAreaStr1.value.find(b'Azazel') >= 0:
        case1 = True
    if len(targetAreaStr2.value) > 0 and targetAreaStr2.value.find((encrypteOutString.value[:50])) >= 0:
        case2 = True
    if len(targetAreaStr3.value) > 0 and targetAreaStr3.value.find(str.encode(encrypteOutStr_SHA256)) >= 0:
        case3 = True
    return case1, case2, case3


if __name__ == '__main__':
    # result = GetChecksumString_SHA256(b"wiejfeijfejfiejfiew32334324234")
    # print(result, type(result))
    try:
        print(check_usbKeyState())
    except Exception as err:
        print(err)

    # targetAreaStr3 = c_char_p(b'\0' * 201)
    # target = create_string_buffer(b'', 201)
    # print(targetAreaStr3.value, type(targetAreaStr3))
    # print(target.value, type(target))
    print(check_usbKeyState())