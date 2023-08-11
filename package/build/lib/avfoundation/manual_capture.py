# coding: utf-8
# Copyright (c) 2018 Jun Hirabayashi (jun@hirax.net)
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php

# Obj-Cクラス読み込み
#from classes.header import *
import ctypes
import objc_util
import time, threading
import os
import numpy as np

# 各種クラスを"objc_util"で読み込む
AVCaptureSession = objc_util.ObjCClass('AVCaptureSession')
AVCaptureDevice = objc_util.ObjCClass('AVCaptureDevice')
AVCaptureDeviceInput = objc_util.ObjCClass('AVCaptureDeviceInput')
AVCapturePhotoOutput = objc_util.ObjCClass('AVCapturePhotoOutput')
AVCaptureVideoPreviewLayer = objc_util.ObjCClass('AVCaptureVideoPreviewLayer')
AVCapturePhotoSettings = objc_util.ObjCClass('AVCapturePhotoSettings')
AVCaptureConnection = objc_util.ObjCClass('AVCaptureConnection')
AVCaptureDeviceDiscoverySession = objc_util.ObjCClass('AVCaptureDeviceDiscoverySession')

# definitions
# https://cnbin.github.io/blog/2015/11/03/avcapturedevice-de-ji-ge-shu-xing/

# AVCaptureDevicePosition
AVCaptureDevicePositionBack = 1  # AVCaptureDevicePositionUnspecified = 0?
AVCaptureDevicePositionFront = 2

# AVCaptureFlashMode
AVCaptureFlashModeOff = 0,
AVCaptureFlashModeOn = 1,
AVCaptureFlashModeAuto = 2

# AVCaptureDevice.h
# typedef NSString *AVCaptureDeviceType NS_STRING_ENUM
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

# VideoOrientation
AVCaptureVideoOrientationPortrait = 1
AVCaptureVideoOrientationPortraitUpsideDown = 2
AVCaptureVideoOrientationLandscapeRight = 3
AVCaptureVideoOrientationLandscapeLeft = 4
# FocusMode
AVCaptureFocusModeLocked = 0
AVCaptureFocusModeAutoFocus = 1
AVCaptureFocusModeContinuousAutoFocus = 2
# ExposureMode
AVCaptureExposureModeLocked = 0
AVCaptureExposureModeAutoExpose = 1
AVCaptureExposureModeContinuousAutoExposure = 2
AVCaptureExposureModeCustom = 3
# WhiteBalanceMode
AVCaptureWhiteBalanceModeLocked = 0
AVCaptureWhiteBalanceModeAutoWhiteBalance = 1
AVCaptureWhiteBalanceModeContinuousAutoWhiteBalance = 2
# TorchMode
AVCaptureTorchModeOff = 0
AVCaptureTorchModeOn = 1
AVCaptureTorchModeAuto = 2

# 下記多分間違ってる
AVMediaTypeVideo = 0
AVMediaTypeAudio = 1
AVMediaTypeText = 2
AVMediaTypeClosedCaption = 3
AVMediaTypeSubtitle = 4
AVMediaTypeTimecode = 5
AVMediaTypeMetadata = 6
AVMediaTypeMuxed = 7

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

# 露出時間設定のため、ctypes.Structureクラス で、CMTime 構造体を用意しておく
CMTimeValue=ctypes.c_int64
CMTimeScale=ctypes.c_int32
CMTimeFlags=ctypes.c_uint32
CMTimeEpoch=ctypes.c_int64
class CMTime(ctypes.Structure):
    _fields_=[('value',CMTimeValue),
              ('timescale',CMTimeScale),
              ('flags',CMTimeFlags),
              ('epoch',CMTimeEpoch)]
    def __init__(self,value=0,timescale=1,flags=0,epoch=0):
        self.value=value
        self.timescale=timescale
        self.flags=flags
        self.epoch=epoch
c.CMTimeMakeWithSeconds.argtypes=[ctypes.c_double,ctypes.c_int32]
c.CMTimeMakeWithSeconds.restype=CMTime
c.CMTimeGetSeconds.argtypes=[CMTime]
c.CMTimeGetSeconds.restype=ctypes.c_double

# ..........................
class AVCaptureWhiteBalanceTemperatureAndTintValues( ctypes.Structure ):
    _fields_=[('temperature',  ctypes.c_float),  # values must be between 1.0 and maxWhiteBalanceGain
              ('tint', ctypes.c_float)]
    def __init__(self,temperature=6000.0,tint=0.0):
        self.temperature=temperature
        self.tint = tint

# ..........................
class CAVCaptureWhiteBalanceGain( ctypes.Structure ):
    _fields_=[('blueGain',  ctypes.c_float),  # values must be between 1.0 and maxWhiteBalanceGain
              ('greenGain', ctypes.c_float),
              ('redGains',  ctypes.c_float)]
    def __init__(self,blueGain=1.0,greenGain=1.0,redGain=1.0):
        self.blueGain=blueGain
        self.greenGain=greenGain
        self.redGain=redGain

# 画像ファイルをアルバムに追加する(Pythonistaのphotos利用)
def addImagefileToAlbum( imagefilePath, albumName ):
    try:
        album = [a for a in photos.get_albums() if a.title == albumName][0]
    except IndexError:
        album = photos.create_album( albumName )
    asset = photos.create_image_asset( imagefilePath )
    album.add_assets( [asset] )

# ===================  マニュアル撮影クラス(作成・即実行) ===================
def manualCapture(
      captureDeviceType,  # カメラのデバイスタイプ
      orientation,
      exposureMode, # AVCaptureExposureModeLocked/AVCaptureExposureModeAutoExpose/AVCaptureExposureModeContinuousAutoExposure/AVCaptureExposureModeCustom
      # The maximum exposure time: iPhone 6 is 1/2 second, 1/3 on iPhone 6s
                  # 1/15, 1/25, 1/45, 1/90, 1/190, 1/380
      exposureValue, exposureScale,  # value/scale (seconds) (CMTimeValue:value = Int62, CMTimeScale:scale = Int32)
      iso,           # min 23 - max 736
      focusMode,     # AVCaptureFocusModeLocked/AVCaptureFocusModeAutoFocus/AVCaptureFocusModeContinuousAutoFocus
      focusDistance, # 0.0 - 1.0
      temperatureAndTint,  # [temprature(kelvin), tint=white balance(-150.0 to +150.0)] ex.[6000.0, 0.0]
      torch,         # [AVCaptureTorchModeOff/AVCaptureTorchModeOn/AVCaptureTorchModeAuto, level(0.0-1.0)]
      fileName,      # fileName used in saving
      albumName,     # album name. if None, image isn't stored to album
      imageFormat,   # '.JPG', '.DNG'
      isSaveNPY ):   # numpy データをマーシャルダンプするか：True, False
    
    # .......... 独自の処理をしたい時のために用意した関数  ..................................
    def processPixelBuffer(pixelData, fileName):
        base_address  = CVPixelBufferGetBaseAddressOfPlane(pixelData, 0)
        bytes_per_row = CVPixelBufferGetBytesPerRowOfPlane(pixelData, 0)
        width = CVPixelBufferGetWidthOfPlane(pixelData, 0)
        height = CVPixelBufferGetHeightOfPlane(pixelData, 0)
        data = np.ctypeslib.as_array(
            ctypes.cast( base_address, ctypes.POINTER( ctypes.c_ushort ) ),
            shape=( ( height, width ) )
            )
        r = data[::2, ::2]
        g = (data[1::2, ::2] + data[::2, 1::2])/2 # G画素値は平均にしちゃう
        b = data[1::2, 1::2];
        # 複数numpyアレイ(r,g,b)をまとめてnpzで保存
        np.savez(fileName+'.npz', r=r, g=g, b=b)
        # 各色のnumpyアレイを、それぞれ保存したい時はこっち
        #np.save(fileName+'.r.npy', r); np.save(fileName+'.g.npy', g); np.save(fileName+'.b.npy', b)
    
    
    # .......... delegate method(共通) 206行で登録..........
    def captureOutput_didFinishProcessingPhoto_error_(_self, _cmd, _output, _photoBuffer, _error):
        # バッファ, 画像取得, ファイル保存
        photoBuffer = objc_util.ObjCInstance( _photoBuffer )
        if not photoBuffer:
            return
        # 画像を保存
        fileData = photoBuffer.fileDataRepresentation()
        if not fileData:
            print('we have no fileDataRepresentation for '+ fileName)
            return
        fileData.writeToFile_atomically_(fileName, True)

        # アルバム保存（アルバムネームがNoneで無かったら）
        if albumName:
            addImagefileToAlbum(fileName, albumName)
            # アルバム登録時はカレントディレクトリのファイルは削除する
            os.remove(fileName)
        # raw 画像が指定されていて、numpy保存指定がされていたら
        if '.DNG'==imageFormat and isSaveNPY:
            _pixelData = photoBuffer.pixelBuffer()
            if not _pixelData:
                return
            CVPixelBufferLockBaseAddress( _pixelData, 0 )
            processPixelBuffer( _pixelData, fileName )
            CVPixelBufferUnlockBaseAddress( _pixelData, 0 )
        event.set()

    # ....... delegate 登録(ここが重要) .......
    CameraManualPhotoCaptureDelegate = objc_util.create_objc_class(
        'CameraManualPhotoCaptureDelegate',   # 作成する delegate クラスの名称
        methods = [captureOutput_didFinishProcessingPhoto_error_], # delegate method
        protocols=['AVCapturePhotoCaptureDelegate']  # プロトコル指定
    )

    # ......................　デバイス設定 .........................................
    # デバイス選択
    # 以前のやり方
    # device = AVCaptureDevice.defaultDeviceWithMediaType_('vide')
    # 最近のやり方
    captureDeviceDiscoverySession = AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
        [ captureDeviceType ], # AVCaptureDeviceTypeBuiltInWideAngleCamera
        AVMediaTypeVideo,
        #AVCaptureDevicePosition.Back )　← 型が違うと言われる
        AVCaptureDevicePositionBack )
        #1 )
    print(AVCaptureDeviceDiscoverySession)

    captureDevices = captureDeviceDiscoverySession.devices()
    print( "Available camera(s): " + str( len( captureDevices ) ) )

    # 該当する最初のデバイスを選択
    device = captureDevices[0]
    
    # デバイスの設定を開始
    device.lockForConfiguration_( None )
    # exposureMode lock/unlock
    if exposureMode and device.isExposureModeSupported_( exposureMode ):
        device.exposureMode = exposureMode
    # exposureDuration and iso
    if exposureValue and exposureScale and iso:
        device.setExposureModeCustomWithDuration_ISO_completionHandler_(
            ( CMTime( exposureValue, exposureScale, 1, 0 ) ),
            iso, None, restype=None, argtypes=[ CMTime, ctypes.c_float, ctypes.c_void_p ] )
    while( not device.isAdjustingExposure ): # 設定を待つ
        time.sleep(0.1)
    #print(device.ISO)
    #focus distance and mode  ( 0.0 - 1.0 )
    if focusDistance and focusMode == AVCaptureFocusModeLocked:
        device.setFocusModeLockedWithLensPosition_completionHandler_( focusDistance, None )
    # focus distance and mode
    if AVCaptureTorchModeOff != torch[0] and device.hasTorch():
        device.torchMode = torch[0]
        device.setTorchModeOnWithLevel_error_( torch[1], None )
    # whitealance
    if temperatureAndTint:
        device.whiteBalanceMode = AVCaptureWhiteBalanceModeLocked
        AVCaptureWhiteBalanceTemperatureAndTintValues
        device.deviceWhiteBalanceGainsForTemperatureAndTintValues_(
            (AVCaptureWhiteBalanceTemperatureAndTintValues(temperatureAndTint[0], temperatureAndTint[1])),
            restype=None,argtypes=[ AVCaptureWhiteBalanceTemperatureAndTintValues ]
        )
    device.unlockForConfiguration()
    time.sleep(0.2)

    # ....... create input, output, and session .......
    _input = AVCaptureDeviceInput.deviceInputWithDevice_error_( device, None )
    photoOutput = AVCapturePhotoOutput.alloc().init()
    time.sleep(0.2)  # デバイスが開かれるのに時間がかかるのでwait

    # AVCaptureSessionを開始
    session = AVCaptureSession.alloc().init()
    session.beginConfiguration()
    session.sessionPreset = 'AVCaptureSessionPresetPhoto'
    if _input:
        session.addInput_( _input )
    else:
        print( 'Failed to get AVCaptureDeviceInput.' )
        return
    if photoOutput:
        session.addOutput_( photoOutput )
    else:
        print( 'Failed to get AVCapturePhotoOutput.' )
        return
    session.commitConfiguration()
    session.startRunning()
    time.sleep(0.2)
    
    availableRawPhotoPixelFormatTypes = photoOutput.availableRawPhotoPixelFormatTypes()
    availableRawPhotoPixelFormatType = int('{}'.format(availableRawPhotoPixelFormatTypes[0]))
    # settings
    settings = None
    if imageFormat == '.DNG': # bayer_RGGB14←OSTypedEnumとしては=1919379252
        settings = AVCapturePhotoSettings.photoSettingsWithRawPixelFormatType( availableRawPhotoPixelFormatType )
    if imageFormat == '.JPG':  # JPGとは限らず、保存設定に準ずる、の動作をするはず
        settings = AVCapturePhotoSettings.photoSettings()
    # 最高解像度で撮影するか
    # settings.isHighResolutionPhotoEnabled = 0 (BOOL 1=true, 0=false)
    settings.AVCaptureFocusMode = focusMode # フォーカスモード
    time.sleep(0.2)
    # delegateを作成し
    event = threading.Event()
    
    delegate = CameraManualPhotoCaptureDelegate.new()
    retain_global(delegate)
    
    # capturePhotoに、setting, delegateを渡して撮影する
    photoOutput.capturePhotoWithSettings_delegate_(settings, delegate)
    
    session.stopRunning()
    session.release()
    photoOutput.release()
