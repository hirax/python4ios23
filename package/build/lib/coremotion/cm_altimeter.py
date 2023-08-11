# coding: utf-8
# Copyright (c) 2018 Jun Hirabayashi (jun@hirax.net)
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php

from classes.header import *
import rubicon_objc
import ctypes
import time

class Altimeter:
    # コンストラクタ
    def __init__(self):
        # 気圧センサはCMAltimeterクラスから取得する
        self.CMAltimeter_ = CMAltimeter.alloc().init()
        if not CMAltimeter.isRelativeAltitudeAvailable():
            print("Altitude is NOT available.")
            raise
        self.create_altitude_handler()
        self.altitude_data = None
        self.create_altitude_handler()
    
    # 気圧センサ値取得用のハンドラー
    def create_altitude_handler(self):
        # ハンドラー関数を作る
        def altitude_f( _data: ctypes.c_void_p, _error: ctypes.c_void_p ) -> None:
            obj = rubicon_objc.api.ObjCInstance(_data) # CMAltitudeData
            self.altitude_data.append(
            {  # デバイス起動からの秒: NSTimeInterval
               'timestamp':rubicon_objc.api.py_from_ns( obj.timestamp ),
               # 相対標高(m): NSNumber
               'relativeAltitude':rubicon_objc.api.py_from_ns( obj.relativeAltitude ),
               # 気圧(kパスカル): NSNumber
               'pressure':rubicon_objc.api.py_from_ns( obj.pressure )
            })
        self.altitude_handler = rubicon_objc.api.Block(altitude_f)

    # 気圧センサ値取得の開始
    def start_relative_altitude_updates(self):
        self.altitude_data = []
        self.CMAltimeter_.startRelativeAltitudeUpdatesToQueue_withHandler_(
            NSOperationQueue.mainQueue,
            self.altitude_handler)
    # 気圧センサ値取得の停止
    def stop_relative_altitude_updates(self):
        self.CMAltimeter_.stopRelativeAltitudeUpdates()
