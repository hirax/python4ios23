# coding: utf-8
# Copyright (c) 2018 Jun Hirabayashi (jun@hirax.net)
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php

import rubicon_objc
import ctypes

UIKit = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/UIKit.framework/UIKit"
)
UIDevice = rubicon_objc.api.ObjCClass('UIDevice')
UIDevice_currentDevice_ = UIDevice.currentDevice

if __name__ == '__main__':
    print(UIDevice_currentDevice_.batteryLevel)
    print(UIDevice_currentDevice_.orientation)
    print(UIDevice_currentDevice_.systemVersion)
    print(UIDevice_currentDevice_.name)
    print(UIDevice_currentDevice_.systemName)
    print(UIDevice_currentDevice_.model)
    print(UIDevice_currentDevice_.localizedModel)
    print(UIDevice_currentDevice_.orientation)
