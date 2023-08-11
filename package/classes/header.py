# coding: utf-8
# Copyright (c) 2018 Jun Hirabayashi (jun@hirax.net)
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php

import ctypes
import enum
import rubicon.objc

#=============== Load Frameworks ==============

CoreLocation = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/CoreLocation.framework/CoreLocation"
)
CoreMotion = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/CoreMotion.framework/CoreMotion"
)
AVFoundation = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/AVFoundation.framework/AVFoundation"
)
AudioToolbox = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/AudioToolbox.framework/AudioToolbox"
)
# =========== Enum ===========================================

class CLLocationAccuracy(enum.Enum):
    kCLLocationAccuracyBest = 0
    kCLLocationAccuracyNearestTenMeters = 1
    kCLLocationAccuracyHundredMeters = 2
    kCLLocationAccuracyKilometer = 3
    kCLLocationAccuracyThreeKilometers = 4

class CLDeviceOrientation(enum.Enum):
    FaceDown = 6 # parallel to the ground and the face is pointing towards the ground.
    FaceUp = 5 # parallel to the ground and the face is pointing towards the sky.
    LandscapeLeft = 3 # in an upright position, with the home button to the right.
    LandscapeRight = 4 # in an upright position, with the home button to the left.
    Portrait = 1 # in an upright position, with the home button towards the ground.
    PortraitUpsideDown = 2 # in an upright position, with the home button towards the sky.
    Unknown = 0 # The device's orientation is unavailable.

class UIDeviceOrientation(enum.Enum):
    unknown = 0
    portrait = 1
    portraitUpsideDown = 2
    landscapeLeft = 3 # homeボタンが右
    landscapeRight = 4 # homeボタンが左
    faceUp = 5
    faceDown = 6

class UIInterfaceOrientation(enum.Enum):
    unknown = 0
    portrait = 1
    portraitUpsideDown = 2
    landscapeLeft = 3
    landscapeRight = 4

class UIImagePickerControllerSourceType(enum.Enum):
    PhotoLibrary = 0
    Camera = 1
    SavedPhotosAlbum = 2

class AVAudioQuality(enum.Enum):
    AVAudioQualityMin = 0
    AVAudioQualityLow = 32
    AVAudioQualityMedium = 64
    AVAudioQualityHigh = 96
    AVAudioQualityMax = 127

class AVFormatIDKey(enum.Enum):  #UInt32
    kAudioFormatLinearPCM      = 1819304813
    kAudioFormatAppleIMA4      = 1768775988
    kAudioFormatMPEG4AAC       = 1633772320
    kAudioFormatMACE3          = 1296122675
    kAudioFormatMACE6          = 1296122678
    kAudioFormatULaw           = 1970037111
    kAudioFormatALaw           = 1634492791
    kAudioFormatMPEGLayer1     = 778924081
    kAudioFormatMPEGLayer2     = 778924082
    kAudioFormatMPEGLayer3     = 778924083
    kAudioFormatAppleLossless  = 1634492771

class AVCaptureDevicePosition(enum.Enum):
    Unspecified = 0
    Back = 1
    Front = 2

class AVCaptureFlashMode(enum.Enum):
    Off = 0  # Never use the flash.
    On = 1   # Always use the flash.
    Auto = 2 # Automatic.

class AVCaptureVideoOrientation(enum.Enum):
    Portrait = 1 # Portrait
    PortraitUpsideDown = 2 # Portrait, upside down.
    LandscapeRight = 3 # Landscape, turned right.
    LandscapeLeft = 4 # Landscape, turned left.

class AVCaptureFocusMode(enum.Enum):
    Locked = 0 #Focus that will not change automatically.
    AutoFocus = 1 # Normal autofocus.
    ContinuousAutoFocus = 2 # Autofocus that attempts to track the subject.

class AVCaptureFocusMode(enum.Enum):
    Locked = 0 # Focus that will not change automatically.
    AutoFocus = 1 # Normal autofocus.
    ContinuousAutoFocus = 2 # Autofocus that attempts to track the subject.

class AVCaptureExposureMode(enum.Enum):
    Locked = 0 # Exposure setting is locked.
    AutoExpose = 1 # The camera performs auto expose.
    ContinuousAutoExposure = 2 # Performs auto-expose and adjusts the setting continously.
    Custom = 3 # Exposure is limited by the ISO and ExposureDuration properties.

class AVCaptureWhiteBalanceMode(enum.Enum):
    Locked = 0 # Auto white balance has been locked.
    AutoWhiteBalance = 1 # Automatic white balance, set it once.
    ContinuousAutoWhiteBalance = 2 # Contimuously evaluate and set the white balance.

class AVCaptureTorchMode(enum.Enum):
    Off = 0 # Never uses the torch.
    On = 1 # Always uses the torch.
    Auto = 2 # Uses the torch based on the available light measured.

class CMMagneticField(ctypes.Structure):
    Uncalibrated = -1 # Magnetic calibration has not occurred.
    Low = 0 # The magnetic calibration was marginal.
    Medium = 1 # The magnetic calibration was of medium quality.
    High = 2 # The magnetic calibration was of high quality.

#========== Constants ================
AVCaptureDeviceTypeExternalUnknown = 'AVCaptureDeviceTypeExternalUnknown'
AVCaptureDeviceTypeBuiltInMicrophone = 'AVCaptureDeviceTypeBuiltInMicrophone'
AVCaptureDeviceTypeBuiltInWideAngleCamera = 'AVCaptureDeviceTypeBuiltInWideAngleCamera'
AVCaptureDeviceTypeBuiltInTelephotoCamera = 'AVCaptureDeviceTypeBuiltInTelephotoCamera'
AVCaptureDeviceTypeBuiltInUltraWideCamera = 'AVCaptureDeviceTypeBuiltInUltraWideCamera'
AVCaptureDeviceTypeBuiltInDualCamera = 'AVCaptureDeviceTypeBuiltInDualCamera'
AVCaptureDeviceTypeBuiltInDualWideCamera = 'AVCaptureDeviceTypeBuiltInDualWideCamera'
AVCaptureDeviceTypeBuiltInTripleCamera = 'AVCaptureDeviceTypeBuiltInTripleCamera'
AVCaptureDeviceTypeBuiltInTrueDepthCamera = 'AVCaptureDeviceTypeBuiltInTrueDepthCamera'
AVCaptureDeviceTypeBuiltInDuoCamera = 'AVCaptureDeviceTypeBuiltInDuoCamera'
AVCaptureDeviceTypeBuiltInLiDARDepthCamera = 'AVCaptureDeviceTypeBuiltInLiDARDepthCamera'

BuiltInMicrophone  =  0
BuiltInTelephotoCamera  =  2
#BuiltInDuoCamera  =  3
BuiltInDualCamera  =  4
BuiltInTrueDepthCamera  =  5

# 下記多分間違ってる
AVMediaTypeVideo = 0
AVMediaTypeAudio = 1
AVMediaTypeText = 2
AVMediaTypeClosedCaption = 3
AVMediaTypeSubtitle = 4
AVMediaTypeTimecode = 5
AVMediaTypeMetadata = 6
AVMediaTypeMuxed = 7

AVMediaTypeVideo = 'vide'

# PixelBuffer Definitions
c = ctypes.cdll.LoadLibrary(None)
CVPixelBufferLockBaseAddress = c.CVPixelBufferLockBaseAddress
CVPixelBufferLockBaseAddress.argtypes = [ctypes.c_void_p, ctypes.c_int]
CVPixelBufferLockBaseAddress.restype = None

CVPixelBufferUnlockBaseAddress = c.CVPixelBufferUnlockBaseAddress
CVPixelBufferUnlockBaseAddress.argtypes = [ctypes.c_void_p, ctypes.c_int]
CVPixelBufferUnlockBaseAddress.restype = None

CVPixelBufferGetWidthOfPlane = c.CVPixelBufferGetWidthOfPlane
CVPixelBufferGetWidthOfPlane.argtypes = [ctypes.c_void_p, ctypes.c_int]
CVPixelBufferGetWidthOfPlane.restype = ctypes.c_int

CVPixelBufferGetHeightOfPlane = c.CVPixelBufferGetHeightOfPlane
CVPixelBufferGetHeightOfPlane.argtypes = [ctypes.c_void_p, ctypes.c_int]
CVPixelBufferGetHeightOfPlane.restype = ctypes.c_int

CVPixelBufferGetBaseAddressOfPlane = c.CVPixelBufferGetBaseAddressOfPlane
CVPixelBufferGetBaseAddressOfPlane.argtypes = [ctypes.c_void_p, ctypes.c_int]
CVPixelBufferGetBaseAddressOfPlane.restype = ctypes.c_void_p

CVPixelBufferGetBytesPerRowOfPlane = c.CVPixelBufferGetBytesPerRowOfPlane
CVPixelBufferGetBytesPerRowOfPlane.argtypes = [ctypes.c_void_p, ctypes.c_int]
CVPixelBufferGetBytesPerRowOfPlane.restype = ctypes.c_int

#=============== Structure definitions =========
# to asign appropriate "type" of Structure for "message"
def member(obj, message, type):
    return rubicon.objc.send_message(obj, message, restype=type, argtypes=[])

def sm(obj, message, type):
    return rubicon.objc.send_message(obj, message, restype=type, argtypes=[])

#class CMAltitudeData(Structure): # CMLogItem
#    _fields_ = [ ('timestamp', c_double),        # timestamp
#                 ('relativeAltitude', c_double), # m
#                 ('pressure', c_double) ]        # k pascal

class CMAcceleration(ctypes.Structure):
    _fields_ = [ ('x', ctypes.c_double),   # m/s^2.
                 ('y', ctypes.c_double),   # m/s^2.
                 ('z', ctypes.c_double) ]  # m/s^2.

class CMRotationRate(ctypes.Structure):
    _fields_ = [ ('x', ctypes.c_double),   # rad/s
                 ('y', ctypes.c_double),   # rad/s
                 ('z', ctypes.c_double) ]  # rad/s

class CMAcceleration(ctypes.Structure):
    _fields_ = [ ('x', ctypes.c_double),   # m/s^2.
                 ('y', ctypes.c_double),   # m/s^2.
                 ('z', ctypes.c_double) ]  # m/s^2.

class CMMagneticField(ctypes.Structure):
    _fields_ = [ ('x', ctypes.c_double),   # microtesla
                 ('y', ctypes.c_double),   # microtesla
                 ('z', ctypes.c_double) ]  # microtesla

class CMMagneticField(ctypes.Structure):
    _fields_ = [ ('field', CMMagneticField),
                 ('accuracy', ctypes.c_int)]  # CMMagneticFieldCalibrationAccuracy

XArbitraryCorrectedZVertical=2
XArbitraryZVertical=1
XMagneticNorthZVertical=4
XTrueNorthZVertical=8

# ..........................
class AVCaptureWhiteBalanceTemperatureAndTintValues( ctypes.Structure ):
    _fields_=[('temperature',  ctypes.c_float),  # values must be between 1.0 and maxWhiteBalanceGain
              ('tint', ctypes.c_float)]
    def __init__(self,temperature = 6000.0, tint = 0.0):
        self.temperature = temperature
        self.tint = tint

# ..........................
class CAVCaptureWhiteBalanceGain(ctypes.Structure):
    _fields_=[('blueGain',  ctypes.c_float),  # values must be between 1.0 and maxWhiteBalanceGain
              ('greenGain', ctypes.c_float),
              ('redGains',  ctypes.c_float)]
    def __init__(self,blueGain=1.0,greenGain=1.0,redGain=1.0):
        self.blueGain=blueGain
        self.greenGain=greenGain
        self.redGain=redGain

# 型定義
CMTimeValue = ctypes.c_int64
CMTimeScale = ctypes.c_int32
CMTimeFlags = ctypes.c_uint32
CMTimeEpoch = ctypes.c_int64

class CMTime(ctypes.Structure):
    _fields_=[('value', CMTimeValue),
              ('timescale', CMTimeScale),
              ('flags',CMTimeFlags),
              ('epoch',CMTimeEpoch)]
    def __init__(self, value = 0, timescale = 1, flags = 0, epoch = 0):
        self.value = value
        self.timescale = timescale
        self.flags = flags
        self.epoch = epoch

# メインプログラムのシンボル→プログラム起動時にロードされた全共有オブジェクト→
# dlopen()のRTLD_GLOBALのフラグでロードされたすべての共有オブジェクトを検索
c = ctypes.cdll.LoadLibrary(None)

# Function(CMTimeMakeWithSeconds, CMTimeGetSeconds etc.)について、引数・返値を設定する
c.CMTimeMakeWithSeconds.argtypes = [ctypes.c_double, ctypes.c_int32]
c.CMTimeMakeWithSeconds.restype = CMTime
c.CMTimeGetSeconds.argtypes = [CMTime]
c.CMTimeGetSeconds.restype = ctypes.c_double

#=============== Load Classes ==============


NSOperationQueue = rubicon.objc.api.ObjCClass('NSOperationQueue')

CMMotionManager = rubicon.objc.api.ObjCClass('CMMotionManager')
CMDeviceMotion = rubicon.objc.api.ObjCClass('CMDeviceMotion')
CMAccelerometerData = rubicon.objc.api.ObjCClass('CMAccelerometerData')

CMAltimeter = rubicon.objc.api.ObjCClass('CMAltimeter')
CMAttitude = rubicon.objc.api.ObjCClass('CMAttitude')
# timestamp: NSTimeInterval: デバイス起動からの秒
# relativeAltitude: NSTimeInterval: 相対標高(m)
# pressure: NSNumber: 気圧(kパスカル)

AVCaptureSession = rubicon.objc.api.ObjCClass('AVCaptureSession')
AVCaptureConnection = rubicon.objc.api.ObjCClass('AVCaptureConnection')
AVCaptureDevice = rubicon.objc.api.ObjCClass('AVCaptureDevice')
AVCaptureDeviceInput = rubicon.objc.api.ObjCClass('AVCaptureDeviceInput')
AVCapturePhotoOutput = rubicon.objc.api.ObjCClass('AVCapturePhotoOutput')
AVCaptureVideoPreviewLayer = rubicon.objc.api.ObjCClass('AVCaptureVideoPreviewLayer')
AVCapturePhotoSettings = rubicon.objc.api.ObjCClass('AVCapturePhotoSettings')
AVCaptureDeviceDiscoverySession = rubicon.objc.api.ObjCClass('AVCaptureDeviceDiscoverySession')


CIFilter = rubicon.objc.api.ObjCClass('CIFilter')
CIVector = rubicon.objc.api.ObjCClass('CIVector')
CIColor = rubicon.objc.api.ObjCClass('CIColor')
CIImage = rubicon.objc.api.ObjCClass('CIImage')
#CGImage = rubicon.objc.api.ObjCClass('CGImage')

