# coding: utf-8
# Jun Hirabayashi (jun@hirax.net, twitter @hirax)
# This code is based on Brun0oO's work(MIT License)

# 本コードではImamgeIOフレームワーク機能を使うが、
# Objc_utilモジュール/IImageクラスでkCIImageAuxiliaryDepthデータを抽出するコードも見ておくべき
# [BreadcrumbsPythonista-Extract-Depthmap](https://github.com/jankais3r/Pythonista-Extract-Depthmap/blob/main/extract_depthmap.py)

import ctypes
import rubicon.objc
from os.path import abspath
import numpy as np

# 定数設定
kCGImageAuxiliaryDataTypeHDRGainMap = 'kCGImageAuxiliaryDataTypeHDRGainMap'
kCGImageAuxiliaryDataTypeDisparity = 'kCGImageAuxiliaryDataTypeDisparity'
kCGImageAuxiliaryDataTypePortraitEffectsMatte = 'kCGImageAuxiliaryDataTypePortraitEffectsMatte'
kCGImageAuxiliaryDataTypeSemanticSegmentationGlassesMatte = 'kCGImageAuxiliaryDataTypeSemanticSegmentationGlassesMatte'
kCGImageAuxiliaryDataTypeSemanticSegmentationGlassesMatte = 'kCGImageAuxiliaryDataTypeSemanticSegmentationGlassesMatte'
kCGImageAuxiliaryDataTypeSemanticSegmentationHairMatte = 'kCGImageAuxiliaryDataTypeSemanticSegmentationHairMatte'
kCGImageAuxiliaryDataTypeSemanticSegmentationSkinMatte = 'kCGImageAuxiliaryDataTypeSemanticSegmentationSkinMatte'
kCGImageAuxiliaryDataTypeSemanticSegmentationSkyMatte = 'kCGImageAuxiliaryDataTypeSemanticSegmentationSkyMatte'
kCGImageAuxiliaryDataTypeSemanticSegmentationTeethMatte = 'kCGImageAuxiliaryDataTypeSemanticSegmentationTeethMatte'

kCGImageAuxiliaryDataInfoData = 'kCGImageAuxiliaryDataInfoData'
kCGImageAuxiliaryDataInfoDataDescription = 'kCGImageAuxiliaryDataInfoDataDescription'

# フレームワークを読み込む
c = ctypes.cdll.LoadLibrary(None)
# CGImageSourceCreateWithURL
ImageIO = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/ImageIO.framework/ImageIO"
)
CoreImage = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/CoreImage.framework/CoreImage"
)

# CFURLCreateFileReferenceURL
CoreFoundation = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
)
CoreData = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/CoreData.framework/CoreData"
)
Foundation = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/Foundation.framework/Foundation"
)
Photos = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/Photos.framework/Photos"
)
CoreGraphics= ctypes.cdll.LoadLibrary(
    "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
)
QuartzCore= ctypes.cdll.LoadLibrary(
    "/System/Library/Frameworks/QuartzCore.framework/QuartzCore"
)
UIKit = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/UIKit.framework/UIKit"
)

# クラス読み込み
NSURL = rubicon.objc.ObjCClass("NSURL")
NSDictionary = rubicon.objc.ObjCClass("NSDictionary")
NSData = rubicon.objc.ObjCClass("NSData")
NSDictionary = rubicon.objc.ObjCClass("NSDictionary")
CIImage = rubicon.objc.ObjCClass("CIImage")
UIImage = rubicon.objc.ObjCClass("UIImage")

# 関数の引数や返り値の型設定
ImageIO.CGImageSourceCreateWithURL.argtypes = [ctypes.c_void_p,
                                               ctypes.c_void_p]
ImageIO.CGImageSourceCreateWithURL.restype = ctypes.c_void_p

ImageIO.CGImageSourceCopyPropertiesAtIndex.argtypes = [ctypes.c_void_p,                                                                 ctypes.c_int,
                                                       ctypes.c_void_p]
ImageIO.CGImageSourceCopyPropertiesAtIndex.restype = ctypes.c_void_p

ImageIO.CGImageSourceCopyAuxiliaryDataInfoAtIndex.argtypes = [ctypes.c_void_p,                                                                 ctypes.c_int,
                                                              ctypes.c_void_p]
ImageIO.CGImageSourceCopyAuxiliaryDataInfoAtIndex.restype = ctypes.c_void_p

def get_imagesource_properties_from_filepath(filepath):
    # まずはURLを作る
    url = NSURL.fileURLWithPath_(abspath(filepath))
    return get_imagesource_properties_from_url(url)

def get_imagesource_properties_data_from_filepath(filepath, auxiliary_data_key):
    # まずはURLを作る
    url = NSURL.fileURLWithPath_(abspath(filepath))
    return get_imagesource_properties_data_from_url(url, auxiliary_data_key)

def get_imagesource_properties_from_url(url):
    # propertiesを得る
    # 下記2行は同じ結果になる
    image_source = ImageIO.CGImageSourceCreateWithURL(url, None)
    #image_source = ImageIO.CGImageSourceCreateWithURL(url.ptr, None)
    # ImageSourceからプロパティを得る
    properties = ImageIO.CGImageSourceCopyPropertiesAtIndex(
                image_source, 0, None)
    properties = rubicon.objc.ObjCInstance(properties)
    return {'properties':properties, 'imagesource':image_source}

def nsdata_to_bytes(data):
    _len = data.length #()
    if _len == 0:
        return b''
    ArrayType = ctypes.c_char * _len
    buffer = ArrayType()
    data.getBytes_length_(ctypes.byref(buffer), _len)
    return buffer[:_len]

def uiimage_to_png(img):
    UIImagePNGRepresentation = c.UIImagePNGRepresentation
    UIImagePNGRepresentation.argtypes = [ctypes.c_void_p]
    UIImagePNGRepresentation.restype = ctypes.c_void_p
    data = rubicon.objc.ObjCInstance(UIImagePNGRepresentation(img))
    return nsdata_to_bytes(data)

def uiimage_to_np(img):
    from PIL import Image
    import io
    memoryFile = io.BytesIO( uiimage_to_png(img) )
    imgOut = Image.open(memoryFile)
    imgOut.load()
    memoryFile.close()
    return np.array(imgOut)

def get_imagesource_properties_data_from_url(url, auxiliary_data_key):
    # propertiesを得る
    properties_and_data = get_imagesource_properties_from_url(url)
    # AuxiliaryDataを得る
    data_info = ImageIO.CGImageSourceCopyAuxiliaryDataInfoAtIndex(
        properties_and_data['imagesource'], 0,
        rubicon.objc.ObjCInstance(rubicon.objc.at(auxiliary_data_key)))
    data_info = rubicon.objc.ObjCInstance(data_info)
    data = data_info[kCGImageAuxiliaryDataInfoData]
    description = data_info[kCGImageAuxiliaryDataInfoDataDescription]
    width = description['Width'].intValue
    bytes_per_row = description['BytesPerRow'].intValue
    height = description['Height'].intValue
    properties_and_data['auxiliary_info'] = data_info
    if auxiliary_data_key is kCGImageAuxiliaryDataTypeHDRGainMap:
        # PixelFormat = 1278226488 -> OneComponent8
        # https://learn.microsoft.com/en-us/dotnet/api/corevideo.cvpixelformattype?view=xamarin-mac-sdk-14
        np_data = np.ctypeslib.as_array(
            ctypes.cast(
            data.bytes,
            ctypes.POINTER(ctypes.c_ubyte)),
            shape=((height, bytes_per_row)) )
        #np_data = np_data[:,:width]
    if auxiliary_data_key is kCGImageAuxiliaryDataTypeDisparity:
        # PixelFormat = 1751411059 -> DisparityFloat16
        np_data = np.ctypeslib.as_array(
            ctypes.cast(
            data.bytes,
            ctypes.POINTER(ctypes.c_int16)),
            shape=((height, width)) )
    # 本来の画像を得る
    #import uikit.ui_uiimage_convert as imconv
    data = NSData.dataWithContentsOfURL_(url)
    uiimage = UIImage.imageWithData_(data)
    properties_and_data['image'] = uiimage_to_np(uiimage)
    #image_data = imconv.ui2np(uiimage)
    properties_and_data['auxiliary_data'] = np_data
    return properties_and_data
