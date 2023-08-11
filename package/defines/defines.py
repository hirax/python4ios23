# Rubicon-objcやObjc_utilを読み込んだ後に、このファイルは読み込む
# (同時読み込みはしない)

import ctypes
# 自動切り替えは、一旦あきらめる
from objc_util.objc_util import *

# Rubicon-objcやObjc_utilを読み込んでいるか
# (同時読み込みはしない)
_is_objc_util = False
_is_rubicon = False
import sys
if 'ObjCClassMethod' in sys.modules:
    _is_objc_util = True
    print('objc_util')

if 'ObjCMethod' in sys.modules:
    _is_rubicon = True
    print('rubicon')

# ---- frameworks -------------
load_framework('ARKit')
load_framework('AVFoundation')
load_framework('SceneKit')
load_framework('SpriteKit')

# フレームワーク読み込み
#AVFoundation = ctypes.cdll.LoadLibrary(
#  "/System/Library/Frameworks/AVFoundation.framework/AVFoundation"
#)

# --- class ---

# Dictionary
NSDictionary = ObjCClass('NSDictionary')
NSMutableDictionary = ObjCClass('NSMutableDictionary')

# ============== AVCapture ==============
AVCaptureSession = ObjCClass('AVCaptureSession')
AVCaptureMultiCamSession = ObjCClass('AVCaptureMultiCamSession')

AVCaptureDevice = ObjCClass('AVCaptureDevice')
AVCaptureDeviceInput = ObjCClass('AVCaptureDeviceInput')
AVCaptureVideoDataOutput = ObjCClass('AVCaptureVideoDataOutput')
AVCaptureDepthDataOutput = ObjCClass('AVCaptureDepthDataOutput')
AVCaptureVideoPreviewLayer = ObjCClass('AVCaptureVideoPreviewLayer')
AVCaptureConnection = ObjCClass('AVCaptureConnection')
AVCaptureDeviceDiscoverySession = ObjCClass('AVCaptureDeviceDiscoverySession')

AVCaptureSynchronizedDataCollection = ObjCClass('AVCaptureSynchronizedDataCollection')

AVCaptureDataOutputSynchronizer = ObjCClass('AVCaptureDataOutputSynchronizer')
AVCaptureSynchronizedDepthData = ObjCClass('AVCaptureSynchronizedDepthData')
AVCaptureSynchronizedSampleBufferData = ObjCClass('AVCaptureSynchronizedSampleBufferData')

AVCaptureDeviceTypeExternalUnknown = 'AVCaptureDeviceTypeExternalUnknown'
AVCaptureDeviceTypeBuiltInMicrophone = 'AVCaptureDeviceTypeBuiltInMicrophone'
AVCaptureDeviceTypeBuiltInWideAngleCamera = 'AVCaptureDeviceTypeBuiltInWideAngleCamera'
AVCaptureDeviceTypeBuiltInTelephotoCamera = 'AVCaptureDeviceTypeBuiltInTelephotoCamera'
AVCaptureDeviceTypeBuiltInUltraWideCamera = 'AVCaptureDeviceTypeBuiltInUltraWideCamera'
AVCaptureDeviceTypeBuiltInDuoCamera = 'AVCaptureDeviceTypeBuiltInDuoCamera'
AVCaptureDeviceTypeBuiltInDualCamera = 'AVCaptureDeviceTypeBuiltInDualCamera'
AVCaptureDeviceTypeBuiltInDualWideCamera = 'AVCaptureDeviceTypeBuiltInDualWideCamera'
AVCaptureDeviceTypeBuiltInTripleCamera = 'AVCaptureDeviceTypeBuiltInTripleCamera'
AVCaptureDeviceTypeBuiltInTrueDepthCamera = 'AVCaptureDeviceTypeBuiltInTrueDepthCamera'
AVCaptureDeviceTypeBuiltInLiDARDepthCamera = 'AVCaptureDeviceTypeBuiltInLiDARDepthCamera'

ARSession = ObjCClass('ARSession')
ARPlaneAnchor = ObjCClass('ARPlaneAnchor')
ARSCNView = ObjCClass('ARSCNView')
ARWorldTrackingConfiguration = ObjCClass('ARWorldTrackingConfiguration')

SCNScene = ObjCClass('SCNScene')
SCNNode = ObjCClass('SCNNode')
SCNAction = ObjCClass('SCNAction')
SCNBox = ObjCClass('SCNBox')
SCNLight = ObjCClass('SCNLight')
SCNSphere = ObjCClass('SCNSphere')
SCNBox = ObjCClass('SCNBox')
SCNCone = ObjCClass('SCNCone')
SCNCapsule = ObjCClass('SCNCapsule')
SCNCylinder = ObjCClass('SCNCylinder')
SCNView = ObjCClass('SCNView')
SCNCamera = ObjCClass('SCNCamera')
SCNMaterial = ObjCClass('SCNMaterial')


ARFrameSemanticSceneDepth = 1 << 3
ARFrameSemanticSmoothedSceneDepth = 1 << 4

AREnvironmentTexturingNone = 0
AREnvironmentTexturingManual = 1
AREnvironmentTexturingAutomatic = 2
    
ARSCNDebugOptionShowFeaturePoints         = 0x40000000
ARSCNDebugOptionShowWorldOrigin   = 0xffffffff80000000
#ARSCNDebugOptionShowWorldTotal    = 0xfffffffffc000000

NSError = ObjCClass('NSError')

UIResponder = ObjCClass('UIResponder')
UIView = ObjCClass('UIView')
UIViewController = ObjCClass('UIViewController')
UIScreen = ObjCClass('UIScreen')
UIColor = ObjCClass('UIColor')

CBAdvertisementDataLocalNameKey = "kCBAdvDataLocalName"
CBAdvertisementDataManufacturerDataKey = "kCBAdvDataManufacturerData" # サポートされていない
CBAdvertisementDataServiceUUIDsKey = "kCBAdvDataServiceUUIDs"

CBAttributePermissionsReadable                    = 0x01
CBAttributePermissionsWriteable                    = 0x02
CBAttributePermissionsReadEncryptionRequired    = 0x04
CBAttributePermissionsWriteEncryptionRequired    = 0x08
    
CBCharacteristicPropertyBroadcast                                                = 0x01
CBCharacteristicPropertyRead                                                    = 0x02
CBCharacteristicPropertyWriteWithoutResponse                                    = 0x04
CBCharacteristicPropertyWrite                                                    = 0x08
CBCharacteristicPropertyNotify                                                    = 0x10
CBCharacteristicPropertyIndicate                                                = 0x20
CBCharacteristicPropertyAuthenticatedSignedWrites                                = 0x40
CBCharacteristicPropertyExtendedProperties                                        = 0x80
#CBCharacteristicPropertyNotifyEncryptionRequired NS_ENUM_AVAILABLE(10_9, 6_0)    = 0x100,
#CBCharacteristicPropertyIndicateEncryptionRequired NS_ENUM_AVAILABLE(10_9, 6_0)    = 0x200
    
# --- enum ---

CBCentralManagerStateUnknown = 0
CBCentralManagerStateResetting = 1
CBCentralManagerStateUnsupported = 2
CBCentralManagerStateUnauthorized = 3
CBCentralManagerStatePoweredOff = 4
CBCentralManagerStatePoweredOn = 5

CBPeripheralManagerStateUnknown = 0
CBPeripheralManagerStateResetting = 1
CBPeripheralManagerStateUnsupported = 2
CBPeripheralManagerStateUnauthorized = 3
CBPeripheralManagerStatePoweredOff = 4
CBPeripheralManagerStatePoweredOn = 5

# AVCaptureDevicePosition
AVCaptureDevicePositionUnspecified = 0
AVCaptureDevicePositionBack = 1
AVCaptureDevicePositionFront = 2

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

AVMediaTypeVideo = 'vide'
AVMediaTypeDepthData = 'dpth'

# AVCaptureSessionPreset
AVCaptureSessionPresetHigh = "AVCaptureSessionPresetHigh"
AVCaptureSessionPresetMedium = "AVCaptureSessionPresetMedium"
AVCaptureSessionPresetLow = "AVCaptureSessionPresetLow"
AVCaptureSessionPreset352x288 = "AVCaptureSessionPreset352x288"
AVCaptureSessionPreset640x480 = "AVCaptureSessionPreset640x480"
AVCaptureSessionPreset1280x720 = "AVCaptureSessionPreset1280x720"
AVCaptureSessionPreset1920x1080 = "AVCaptureSessionPreset1920x1080"
AVCaptureSessionPreset3840x2160 = "AVCaptureSessionPreset3840x2160"
AVCaptureSessionPresetiFrame960x540 = "AVCaptureSessionPresetiFrame960x540"
AVCaptureSessionPresetiFrame1280x720 = "AVCaptureSessionPresetiFrame1280x720"
AVCaptureSessionPresetInputPriority = "AVCaptureSessionPresetInputPriority"

# --- enum --- AVCaptureDeviceType
#https://docs.microsoft.com/ja-jp/dotnet/api/avfoundation.avcapturedevicetype?view=xamarin-ios-sdk-12
BuiltInMicrophone = 0
BuiltInTelephotoCamera = 2
BuiltInDuoCamera = 3 # 使わないようにすること
BuiltInDualCamera = 4 # こちらを使うようにすること
BuiltInTrueDepthCamera = 5

# --- ****

kCVPixelBufferPixelFormatTypeKey = 'PixelFormatType'

kCVPixelFormatType_DisparityFloat16 = 1751411059
kCVPixelFormatType_DisparityFloat32 = 1717856627
kCVPixelFormatType_DepthFloat16 = 1751410032
kCVPixelFormatType_DepthFloat32 = 1717855600

# --- enum --- CVPixelFormatType
#https://learn.microsoft.com/en-us/dotnet/api/corevideo.cvpixelformattype?view=xamarin-mac-sdk-14
Argb2101010LEPacked =   1815162994
CV128RGBAFloat =   1380410945
CV14BayerBggr =   1650943796
CV14BayerGbrg =   1734505012
CV14BayerGrbg =   1735549492
CV14BayerRggb =   1919379252
CV16BE555 =   16
CV16BE565 =   1110783541
CV16Gray =   1647392359
CV16LE555 =   1278555445
CV16LE5551 =   892679473
CV16LE565 =   1278555701
CV1IndexedGray_WhiteIsZero =   33
CV1Monochrome =   1
CV24BGR =   842285639
CV24RGB =   24
CV2Indexed =   2
CV2IndexedGray_WhiteIsZero =   34
CV30RGB =   1378955371
CV30RgbLePackedWideGamut =   1999843442
CV32ABGR =   1094862674
CV32AlphaGray =   1647522401
CV32ARGB =   32
CV32BGRA =   1111970369
CV32RGBA =   1380401729
CV420YpCbCr10BiPlanarFullRange =   2019963440
CV420YpCbCr10BiPlanarVideoRange =   2016686640
CV420YpCbCr8BiPlanarFullRange =   875704422
CV420YpCbCr8BiPlanarVideoRange =   875704438
CV420YpCbCr8Planar =   2033463856
CV420YpCbCr8PlanarFullRange =   1714696752
CV422YpCbCr_4A_8BiPlanar =   1630697081
CV422YpCbCr10 =   1983000880
CV422YpCbCr10BiPlanarFullRange =   2019963442
CV422YpCbCr10BiPlanarVideoRange =   2016686642
CV422YpCbCr16 =   1983000886
CV422YpCbCr8 =   846624121
CV422YpCbCr8_yuvs =   2037741171
CV422YpCbCr8FullRange =   2037741158
CV4444AYpCbCr16 =   2033463606
CV4444AYpCbCr8 =   2033463352
CV4444YpCbCrA8 =   1983131704
CV4444YpCbCrA8R =   1916022840
CV444YpCbCr10 =   1983131952
CV444YpCbCr10BiPlanarFullRange =   2019963956
CV444YpCbCr10BiPlanarVideoRange =   2016687156
CV444YpCbCr8 =   1983066168
CV48RGB =   1647589490
CV4Indexed =   4
CV4IndexedGray_WhiteIsZero =   36
CV64ARGB =   1647719521
CV64RGBAHalf =   1380411457
CV8Indexed =   8
CV8IndexedGray_WhiteIsZero =   40
DepthFloat16 =   1751410032
DepthFloat32  =  1717855600
DisparityFloat16 =   1751411059
DisparityFloat32 =   1717856627
OneComponent16Half =   1278226536
OneComponent32Float =   1278226534
OneComponent8 =   1278226488
TwoComponent16Half =   843264104
TwoComponent32Float =   843264102
TwoComponent8 =   843264056

# AVCaptureDeviceFormat: https://zenn.dev/yorifuji/scraps/bc52d2e4601de0

# ============== UI ==============

UIImage = ObjCClass('UIImage')

# ============== CI ==============
CIImage = ObjCClass('CIImage')

# ============== CMTime ==============
#class CMTime(ctypes.Structure):
#    _fields_ = [
#                ('CMTimeValue', ctypes.c_int64),
#                ('CMTimeScale', ctypes.c_int32),
#                ('CMTimeEpoch', ctypes.c_int64),
#                ('CMTimeFlags', ctypes.c_uint32),
#                ]
#
#def CMTimeMake(value, scale):
#    cm = CMTime()
#    cm.CMTimeScale = scale
#    cm.CMTimeValue = value
#    return cm

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

# dispatch_get_current_queue 関数のポインタ指定、引数型はvoid・返値型定義
dispatch_get_current_queue = c.dispatch_get_current_queue
dispatch_get_current_queue.restype = c_void_p
# CMSampleBufferGetImageBuffer 関数のポインタ指定、引数型・返値型定義
CMSampleBufferGetImageBuffer = c.CMSampleBufferGetImageBuffer
CMSampleBufferGetImageBuffer.argtypes = [c_void_p]
CMSampleBufferGetImageBuffer.restype = c_void_p
# CVPixelBufferLockBaseAddress 関数のポインタ指定、引数型・返値型定義
CVPixelBufferLockBaseAddress = c.CVPixelBufferLockBaseAddress
CVPixelBufferLockBaseAddress.argtypes = [c_void_p, c_int]
CVPixelBufferLockBaseAddress.restype = None

#CVPixelBufferGetBaseAddress
CVPixelBufferGetBaseAddress = c.CVPixelBufferGetBaseAddress
CVPixelBufferGetBaseAddress.argtypes = [ctypes.c_void_p]
CVPixelBufferGetBaseAddress.restype = ctypes.c_int

CVPixelBufferGetWidth = c.CVPixelBufferGetWidth
CVPixelBufferGetWidth.argtypes = [ctypes.c_void_p]
CVPixelBufferGetWidth.restype = ctypes.c_int

CVPixelBufferGetHeight = c.CVPixelBufferGetHeight
CVPixelBufferGetHeight.argtypes = [ctypes.c_void_p]
CVPixelBufferGetHeight.restype = ctypes.c_int

CVPixelBufferGetBytesPerRow = c.CVPixelBufferGetBytesPerRow
CVPixelBufferGetBytesPerRow.argtypes = [ctypes.c_void_p]
CVPixelBufferGetBytesPerRow.restype = ctypes.c_int

# CVPixelBufferUnlockBaseAddress 関数のポインタ指定、引数型・返値型定義
CVPixelBufferUnlockBaseAddress = c.CVPixelBufferUnlockBaseAddress
CVPixelBufferUnlockBaseAddress.argtypes = [c_void_p, c_int]
CVPixelBufferUnlockBaseAddress.restype = None

# PixelBuffer Definitions
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
