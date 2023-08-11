# coding: utf-8
# Copyright (c) 2018 Jun Hirabayashi (jun@hirax.net)
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php


import objc_util.objc_util as objc_util
import ctypes
import enum

class CLLocationAccuracy(enum.Enum):
    kCLLocationAccuracyBest = 0
    kCLLocationAccuracyNearestTenMeters = 1
    kCLLocationAccuracyHundredMeters = 2
    kCLLocationAccuracyKilometer = 3
    kCLLocationAccuracyThreeKilometers = 4

# enum が動かないときのために
kCLLocationAccuracyBest = 0
kCLLocationAccuracyNearestTenMeters = 1
kCLLocationAccuracyHundredMeters = 2
kCLLocationAccuracyKilometer = 3
kCLLocationAccuracyThreeKilometers = 4

CLAuthorizationStatus_AuthorizedAlways = 3
CLAuthorizationStatus_AuthorizedWhenInUse = 4
CLAuthorizationStatus_Denied = 2
CLAuthorizationStatus_NotDetermined = 0
CLAuthorizationStatus_Restricted = 1

# フレームワークを読み込む
CoreLocation = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/CoreLocation.framework/CoreLocation"
)

class LocationManager:
    # コンストラクタ
    def __init__(self, accuracy):
        CLLocationManager = objc_util.ObjCClass('CLLocationManager')
        #CLLocation = objc_util.ObjCClass('CLLocation')
        self.CLLocationManager_ = CLLocationManager.alloc().init()
        self.CLLocationManager_.desiredAccuracy = accuracy
        # authozationStatus はdeprecatedになっています
        if not self.CLLocationManager_.authozationStatus == CLAuthorizationStatus_AuthorizedWhenInUse:
            self.CLLocationManager_.requestAlwaysAuthorization()
        self.location = None
        self.heading = None

    def create_delegate(self):  #delegateを作る
        def locationManager_didUpdateLocations_(
            _self,_cmd,_manager,_locations):
            pass
        # delegateを作成する
        LocationManagerDelegate = objc_util.create_objc_class(
            # 作成する delegate クラスの名称
            'LocationManagerDelegate',
            # delegate 関数とプロトコルを指定する
            methods = [locationManager_didUpdateLocations_],
            protocols=['CLLocationManagerDelegate'])
        CLLocationManagerDelegate_ = LocationManagerDelegate.new()
        objc_util.retain_global(CLLocationManagerDelegate_)

        # CLLocationManagerインスタンスに、delegateインスタンスを登録
        self.CLLocationManager_.delegate = CLLocationManagerDelegate_

    # 「位置や向きに関する情報取得を開始する」メソッド
    def start_update_location_and_heading(self):
        self.CLLocationManager_.startUpdatingLocation()
        self.CLLocationManager_.startUpdatingHeading()

    # 「位置や向きに関する情報取得を停止する」メソッド
    def stop_update_location_and_heading(self):
        self.CLLocationManager_.stopUpdatingLocation()
        self.CLLocationManager_.stopUpdatingHeading()

    # 「位置や移動方向を取得する」メソッド
    def request_location_and_heading(self):
        loc = self.CLLocationManager_.location()
        hed = self.CLLocationManager_.heading()
        if loc:
            self.location = {
            'timestamp':str(loc.timestamp().description()),
            'coordinate':{'latitude':loc.coordinate().a,
                      'longitude':loc.coordinate().b},
            'altitude':loc.altitude(),
            'ellipsoidalAltitude':loc.ellipsoidalAltitude(),
            'floor':loc.floor().level(),
            'horizontalAccuracy':loc.horizontalAccuracy(),
            'verticalAccuracy':loc.verticalAccuracy(),
            'sourceInformation':{"isProducedByAccessory":
                loc.sourceInformation().isProducedByAccessory(),
                             "isSimulatedBySoftware":
                loc.sourceInformation().isProducedByAccessory()}}
        if hed:
            self.heading = {
                'timestamp':str(hed.timestamp().description()),
                'x':hed.x(),
                'y':hed.y(),
                'z':hed.z(),
                #'CLHeadingComponentValue':hed.CLHeadingComponentValue(),
                'magneticHeading':hed.magneticHeading(),
                'trueHeading':hed.trueHeading(),
                'headingAccuracy':hed.headingAccuracy()}
        return self.location, self.heading

# -----------------------
# 場所を問い合わせる
def requestLocation_():
    global CLLocationManager_
    CLLocationManager_.startUpdatingLocation()
    loc = CLLocationManager_.location()
    #heading = CLLocationManager_.heading()
    CLLocationManager_.stopUpdatingLocation()
    
    if loc:
        ret = {
        'timestamp':str(loc.timestamp().description()),
        'coordinate':{'latitude':loc.coordinate().a,
                      'longitude':loc.coordinate().b},
        'altitude':loc.altitude(),
        'ellipsoidalAltitude':loc.ellipsoidalAltitude(),
        'floor':loc.floor().level(),
        'horizontalAccuracy':loc.horizontalAccuracy(),
        'verticalAccuracy':loc.verticalAccuracy(),
        'sourceInformation':{"isProducedByAccessory":
            loc.sourceInformation().isProducedByAccessory(),
                             "isSimulatedBySoftware":
            loc.sourceInformation().isProducedByAccessory()}
    }
    return ret



