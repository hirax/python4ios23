# coding: utf-8
# @omz
# https://forum.omz-software.com/topic/1554/accessing-the-led-flashlight/3

from ctypes import c_void_p, c_char_p, c_int, c_bool, cdll

AVFoundation = cdll.LoadLibrary(
  "/System/Library/Frameworks/AVFoundation.framework/AVFoundation"
)

# ランタイムを読み込む
objc = cdll.LoadLibrary(None)
# クラス名からobjcクラスを得る
objc.objc_getClass.argtypes = [c_char_p]
objc.objc_getClass.restype = c_void_p
# セレクタ名からセレクタを得る
objc.sel_registerName.restype = c_void_p
objc.sel_registerName.argtypes = [c_char_p]

# メッセージを投げて、結果を得るためのヘルパー関数
def msg(obj, restype, sel, argtypes=None, *args):
    if argtypes is None:
        argtypes = []
    # objc_msgSendの引数型と返り値型を与える（引数の先頭２つは、obj, セレクタ名）
    objc.objc_msgSend.argtypes =  [c_void_p, c_void_p] + argtypes
    objc.objc_msgSend.restype = restype
    # メッセージを投げる
    res = objc.objc_msgSend(obj, objc.sel_registerName(sel), *args)
    return res
    
# objcクラスへのリファレンスを得る
def cls(cls_name):
    return objc.objc_getClass(cls_name)

# バイト列=UTF8文字を、NSStringにして返す（Python 3との違いを吸収）
def nsstr(s):
    return msg( cls(b'NSString'),
                c_void_p,   # 返り値型
                b'stringWithUTF8String:',
                [c_char_p], # 引数型
                s)          # 変換したいバイト列

# ライトの点灯・非点灯状態を指定する
def setTorchMode(state=0): # 1:turn on, 0 turn off
    # AVCaptureDevice（defaultDeviceWithMediaType）を得る
    AVCaptureDevice = cls(b'AVCaptureDevice')
    device = msg( AVCaptureDevice, c_void_p,
                  b'defaultDeviceWithMediaType:',
                  [c_void_p], nsstr(b'vide'))
    # 得たデバイスにライトがあれば(hasTorch=True)
    has_torch = msg(device, c_bool, b'hasTorch')
    if not has_torch:
        raise RuntimeError(b'Device has no flashlight')
    # Configurationロックして、設定変更する
    msg(device, None, b'lockForConfiguration:', [c_void_p], None)
    msg(device, None, b'setTorchMode:', [c_int], state)
    msg(device, None, b'unlockForConfiguration')

# ライトの点灯・非点灯状態を入れ替える
def toggle_flashlight():
    AVCaptureDevice = cls( b'AVCaptureDevice' )
    device = msg(AVCaptureDevice, c_void_p, b'defaultDeviceWithMediaType:', [c_void_p], nsstr(b'vide'))
    has_torch = msg(device, c_bool, b'hasTorch')
    if not has_torch:
        raise RuntimeError(b'Device has no flashlight')
    current_mode = msg(device, c_int, b'torchMode')
    mode = 1 if current_mode == 0 else 0
    msg(device, None, b'lockForConfiguration:', [c_void_p], None)
    msg(device, None, b'setTorchMode:', [c_int], mode)
    msg(device, None, b'unlockForConfiguration')

if __name__ == '__main__':
    toggle_flashlight()

