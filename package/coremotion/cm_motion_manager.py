# coding: utf-8
# Copyright (c) 2018 Jun Hirabayashi (jun@hirax.net)
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php

from classes.header import *
import rubicon.objc
import ctypes
import time

class MotionManager:
    # コンストラクタ
    def __init__(self):
        self.CMMotionManager_ = CMMotionManager.alloc().init()
        if not self.CMMotionManager_.isAccelerometerAvailable():
            print("Accelerometer in NOT Available.")
            raise
        self.accelerometer_data = None
        self.create_accelerometer_handler()
        self.magnetic_field_data = None
        self.create_magnetic_field_handler()
        self.altitude_data = None
        self.create_altitude_handler()
    
    # ------加速度センサ値取得------
    # 加速度センサ値取得用ハンドラー
    def create_accelerometer_handler(self):
        # ハンドラー関数を作る
        def accelerometer_f( _data: ctypes.c_void_p, _error: ctypes.c_void_p ) -> None:
            obj = rubicon.objc.api.ObjCInstance( _data ) # CMAccelerationData
            # CMAcceleration は構造体なので、返り値の型を指定した上で、メンバの値を得る
            acc = member(obj, 'acceleration', CMAcceleration)
            # 'timestamp' は構造体で無く基本型なので、下記は不要なはず
            ts = member(obj,'timestamp', ctypes.c_double) # NSTimeInterval(s) from booting
            self.accelerometer_data.append( {'x':acc.x, 'y':acc.y, 'z':acc.z, 'at':ts} )
            # blockを作る
        self.accelerometer_handler = rubicon.objc.api.Block(accelerometer_f)
    
    # 加速度センサ値取得の開始
    def start_accelerometer_updates(self, update_inteval): # 単位は秒
        self.accelerometer_data = []
        self.CMMotionManager_.accelerometerUpdateInterval = update_inteval
        self.CMMotionManager_.startAccelerometerUpdatesToQueue_withHandler_(
            NSOperationQueue.mainQueue,
            self.accelerometer_handler)
    
    # 加速度センサ値取得の停止
    def stop_accelerometer_updates(self):
        self.CMMotionManager_.stopAccelerometerUpdates()

    # -------磁気センサ値取得-------
    # 磁気センサ値取得用のハンドラー
    def create_magnetic_field_handler(self):
        # ハンドラー関数を作る
        def magnetic_field_f( _data: ctypes.c_void_p, _error: ctypes.c_void_p ) -> None:
            obj = rubicon.objc.api.ObjCInstance( _data ) # CMMagnetometerData
            magneticField = member(obj, 'magneticField', CMMagneticField)
            self.magnetic_field_data.append(
                {'x':magneticField.field.x,
                 'y':magneticField.field.y,
                 'z':magneticField.field.z} )
        self.magnetic_field_handler = rubicon.objc.api.Block(magnetic_field_f)
    
    # 磁気センサ値取得の開始
    def start_magnetic_field_updates(self, update_inteval): # 単位は秒
        self.magnetic_field_data = []
        self.CMMotionManager_.deviceMotionUpdateInterval = update_inteval
        self.CMMotionManager_.startDeviceMotionUpdatesUsingReferenceFrame_toQueue_withHandler_(
            XArbitraryCorrectedZVertical,
            NSOperationQueue.mainQueue,
            self.magnetic_field_handler )
        
    # 磁気センサ値取得の停止
    def stop_magnetic_field_updates(self):
        self.CMMotionManager_.stopDeviceMotionUpdates()
    
    # -------気圧センサ値取得-------
    # 気圧センサ値取得用のハンドラー
    def create_altitude_handler(self):
        # 気圧センサはCMAltimeterクラスから取得する
        self.CMAltimeter_ = CMAltimeter.alloc().init()
        if not CMAltimeter.isRelativeAltitudeAvailable():
            print("Altitude is NOT available.")
            raise
        # ハンドラー関数を作る
        def altitude_f( _data: ctypes.c_void_p, _error: ctypes.c_void_p ) -> None:
            obj = rubicon.objc.api.ObjCInstance( _data )
            self.altitude_data.append(
            {  # デバイス起動からの秒: NSTimeInterval
               'timestamp':rubicon.objc.api.py_from_ns( obj.timestamp ),
               # 相対標高(m): NSNumber
               'relativeAltitude':rubicon.objc.api.py_from_ns( obj.relativeAltitude ),
               # 気圧(kパスカル): NSNumber
               'pressure':rubicon.objc.api.py_from_ns( obj.pressure )
            })
        self.altitude_handler = rubicon.objc.api.Block(altitude_f)
    # 気圧センサ値取得の開始
    def start_relative_altitude_updates(self):
        self.altitude_data = []
        self.CMAltimeter_.startRelativeAltitudeUpdatesToQueue_withHandler_(
            NSOperationQueue.mainQueue,
            self.altitude_handler)
    # 気圧センサ値取得の停止
    def stop_relative_altitude_updates(self):
        self.CMAltimeter_.stopRelativeAltitudeUpdates()

    # -------CMDeviceMotion値取得-------
    def get_device_motion(self):
        data = self.CMMotionManager_.deviceMotion
        # （Classでなく）structのpropertyに対してはメッセージを投げる
        deviceMotionData = {
            'attitude':data.attitude,
            'rotationRate':member(data, "rotationRate", CMRotationRate),
            'gravity':member(data, "gravity", CMAcceleration),
            'userAcceleration':member(data, "userAcceleration", CMAcceleration),
            'magneticField':member(data, "magneticField", CMMagneticField),
            'heading':data.heading,
            'sensorLocation':data.sensorLocation }
        return deviceMotionData
    
    # CMDeviceMotion値取得の開始
    def start_device_motion_updates(self):
        self.CMMotionManager_.startDeviceMotionUpdates()
        self.CMMotionManager_.showsDeviceMovementDisplay = True

    # CMDeviceMotion値取得の停止
    def stop_device_motion_updates(self):
        self.CMMotionManager_.stopDeviceMotionUpdates()

