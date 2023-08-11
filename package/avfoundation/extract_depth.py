# coding: utf-8
# c.f. https://forum.omz-software.com/topic/3365/photos-module-start-camera-from-button/26

from objc_util.objc_util import *
import ctypes
import os
import shutil

from uikit.ui_uiview import *

MobileCoreServices = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/MobileCoreServices.framework/MobileCoreServices"
)

# CGImageSourceCreateWithURL
ImageIO = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/ImageIO.framework/ImageIO"
)

# CFURLCreateFileReferenceURL
CoreFoundation = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
)

Foundation = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/Foundation.framework/Foundation"
)

Photos = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/Photos.framework/Photos"
)

PHAsset = ObjCClass('PHAsset')

#load_framework('MobileCoreServices')
#load_framework('ImageIO')
#load_framework('CoreFoundation')

kCGImageAuxiliaryDataTypePortraitEffectsMatte = 'kCGImageAuxiliaryDataTypePortraitEffectsMatte'

# フォトアルバムから静止画を取得する場合
@on_main_thread
def pick_photoalbum_and_save(file_path):
    # 撮影後に呼ばれるdelegateを定義
    def imagePickerController_didFinishPickingMediaWithInfo_(self, cmd, picker, info):
        pick = ObjCInstance(picker)
        pick.setDelegate_(None)  # Set delegate to nil, and release its memory:
        ObjCInstance(self).release()
        pick.dismissViewControllerAnimated_completion_(True, None) # Dismiss the sheet:
        
        # c.f.
        # https://dev.classmethod.jp/articles/ios8-photo-kit-8/
        #  Assets Library frameworkが提供するURLにアクセスする
        infos = ObjCInstance(info)  # Get UIImage
        
        url = infos['UIImagePickerControllerReferenceURL']
        print(url)
        
        # URLからPHAssetを取得
        results = PHAsset.fetchAssetsWithALAssetURLs_options_([url], None)
        print(results[0])
        
        #print(results[0].creationDate.description)
        #PHFetchResult *fetchResult = [PHAsset fetchAssetsWithALAssetURLs:@[url,] options:nil];
        #PHAsset *asset = fetchResult.firstObject;
    
        #img = infos['UIImagePickerControllerOriginalImage']
        #url = infos['UIImagePickerControllerImageURL']
        #print(url)
        #print(type(url))
        
        # https://stackoverflow.com/questions/50240637/getting-depth-data-from-uiimagepickercontroller
        
        #source = ImageIO.CGImageSourceCreateWithURL(url, None)
        #print(source)
        
        #urlref = Foundation.CFBridgingRetain(nsurl(url))
        #        source = ImageIO.CGImageSourceCreateWithURL(url, None)
        #
        # https://developer.apple.com/documentation/avfoundation/avportraiteffectsmatte/extracting_portrait_effects_matte_image_data_from_a_photo?language=objc
        
        # 次で落ちている
        #url = CoreFoundation.CFURLCreateFileReferenceURL(url)
        #print(url)
        #print(type(url))
        #source = ImageIO.CGImageSourceCreateWithURL(url, None)
        #print(source)
        
        #auxiliaryInfoDict = ImageIO.CGImageSourceCopyAuxiliaryDataInfoAtIndex(source, 0, kCGImageAuxiliaryDataTypePortraitEffectsMatte)
        #print(auxiliaryInfoDict)
        
        #auxiliaryInfoDict = CGImageSourceCopyAuxiliaryDataInfoAtIndex(source, 0, kCGImageAuxiliaryDataTypePortraitEffectsMatte);
    
        #if '.jpg' == os.path.splitext(file_path)[1].lower():
        #    #img.jpegData()
        #    # UIImageJPEGRepresentationの引数・返値型を指定する
        #    func = c.UIImageJPEGRepresentation
        #    func.argtypes = [ctypes.c_void_p, ctypes.c_float]
        #    func.restype = ctypes.c_void_p
        #    # UIImageJPEGRepresentationでJPEGとしてファイル保存
        #    ui_image_ = ObjCInstance( func(img.ptr, 1.0) )
        #elif '.png' == os.path.splitext(file_path)[1].lower():
        #    # UIImagePNGRepresentationの引数・返値型を指定する
        #    func = c.UIImagePNGRepresentation
        #    func.argtypes = [ctypes.c_void_p]
        #    func.restype = ctypes.c_void_p
        #    # UIImagePNGRepresentationでPNGとしてファイル保存
        #    ui_image_ = ObjCInstance( func(img.ptr) )
        #ui_image_.writeToFile_atomically_(file_path, True)
    
    # UIImagePickerControllerDelegate を登録する
    MyPickerDelegate = create_objc_class(
        'MyPickerDelegate',
        methods=[imagePickerController_didFinishPickingMediaWithInfo_],
        protocols=['UIImagePickerControllerDelegate']
    )
    # UIImagePickerController とdelegateを生成して、delegatを登録
    picker = ObjCClass('UIImagePickerController').alloc().init() # Show camera
    delegate = MyPickerDelegate.alloc().init()
    picker.setDelegate_(delegate)
    picker.allowsEditing = False
    # 0: UIImagePickerControllerSourceTypePhotoLibrary
    # 1: UIImagePickerControllerSourceTypeCamera
    # 2: UIImagePickerControllerSourceTypeSavedPhotoAlbum
    picker.sourceType = 2
    # 自分ViewからUIImagePickerControllerを呼ぶ
    vc = get_topcontroler()
    vc.presentModalViewController_animated_(picker, True)
