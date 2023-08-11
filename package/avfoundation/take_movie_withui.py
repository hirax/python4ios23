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

# 動画を取得する場合
@on_main_thread
def take_movie_and_save(file_path):
    # 撮影後に呼ばれるdelegateを定義
    def imagePickerController_didFinishPickingMediaWithInfo_(self, cmd, picker, info):
        pick = ObjCInstance(picker)
        pick.setDelegate_(None)     # Set delegate to nil, and release its memory:
        ObjCInstance(self).release()
        pick.dismissViewControllerAnimated_completion_(True, None) # Dismiss the sheet:
        infos = ObjCInstance(info)  # Get UIImage
        url = infos['UIImagePickerControllerMediaURL']
        shutil.copy("{}".format(url.path()), file_path)
    # UIImagePickerControllerDelegateクラスを登録する
    MyPickerDelegate = create_objc_class(
        'MyPickerDelegate',
        methods=[imagePickerController_didFinishPickingMediaWithInfo_],
        protocols=['UIImagePickerControllerDelegate']
    )
    # UIImagePickerController とdelegateクラスのインスタンスを生成
    UIImagePickerController = ObjCClass('UIImagePickerController')
    picker = UIImagePickerController.alloc().init() # Show camera
    delegate = MyPickerDelegate.alloc().init()
    picker.setDelegate_(delegate)
    picker.allowsEditing = False
    # 0: UIImagePickerControllerSourceTypePhotoLibrary
    # 1: UIImagePickerControllerSourceTypeCamera
    # 2: UIImagePickerControllerSourceTypeSavedPhotoAlbum
    picker.sourceType = 1
    picker.mediaTypes = UIImagePickerController.availableMediaTypesForSourceType_(1)
    vc = get_topcontroler()
    vc.presentModalViewController_animated_(picker, True)

# 静止画を取得する場合
@on_main_thread
def take_photo_and_save(file_path):
    # 撮影後に呼ばれるdelegateを定義
    def imagePickerController_didFinishPickingMediaWithInfo_(self, cmd, picker, info):
        pick = ObjCInstance(picker)
        pick.setDelegate_(None)  # Set delegate to nil, and release its memory:
        ObjCInstance(self).release()
        pick.dismissViewControllerAnimated_completion_(True, None) # Dismiss the sheet:
        infos = ObjCInstance(info)  # Get UIImage
        #img = infos['UIImagePickerControllerEditedImage']
        img = infos['UIImagePickerControllerOriginalImage']
        if '.jpg' == os.path.splitext(file_path)[1].lower():
            #img.jpegData()
            # UIImageJPEGRepresentationの引数・返値型を指定する
            func = c.UIImageJPEGRepresentation
            func.argtypes = [ctypes.c_void_p, ctypes.c_float]
            func.restype = ctypes.c_void_p
            # UIImageJPEGRepresentationでJPEGとしてファイル保存
            ui_image_ = ObjCInstance( func(img.ptr, 1.0) )
        elif '.png' == os.path.splitext(file_path)[1].lower():
            # UIImagePNGRepresentationの引数・返値型を指定する
            func = c.UIImagePNGRepresentation
            func.argtypes = [ctypes.c_void_p]
            func.restype = ctypes.c_void_p
            # UIImagePNGRepresentationでPNGとしてファイル保存
            ui_image_ = ObjCInstance( func(img.ptr) )
        ui_image_.writeToFile_atomically_(file_path, True)
    # UIImagePickerControllerDelegateクラスを登録する
    MyPickerDelegate = create_objc_class(
        'MyPickerDelegate',
        methods=[imagePickerController_didFinishPickingMediaWithInfo_],
        protocols=['UIImagePickerControllerDelegate']
    )
    # UIImagePickerController とdelegateクラスのインスタンスを生成
    picker = ObjCClass('UIImagePickerController').alloc().init() # Show camera
    delegate = MyPickerDelegate.alloc().init()
    picker.setDelegate_(delegate)
    picker.allowsEditing = False
    # 0: UIImagePickerControllerSourceTypePhotoLibrary
    # 1: UIImagePickerControllerSourceTypeCamera
    # 2: UIImagePickerControllerSourceTypeSavedPhotoAlbum
    picker.sourceType = 1
    
    # 自分ViewからUIImagePickerControllerを呼ぶ
    vc = get_topcontroler()
    vc.presentModalViewController_animated_(picker, True)

# フォトライブラリーから静止画を取得する場合
@on_main_thread
def pick_photolibrary_and_save(file_path):
    # 撮影後に呼ばれるdelegateを定義
    def imagePickerController_didFinishPickingMediaWithInfo_(self, cmd, picker, info):
        pick = ObjCInstance(picker)
        pick.setDelegate_(None)  # Set delegate to nil, and release its memory:
        ObjCInstance(self).release()
        pick.dismissViewControllerAnimated_completion_(True, None) # Dismiss the sheet:
        infos = ObjCInstance(info)  # Get UIImage
        #img = infos['UIImagePickerControllerEditedImage']
        img = infos['UIImagePickerControllerOriginalImage']
        if '.jpg' == os.path.splitext(file_path)[1].lower():
            #img.jpegData()
            # UIImageJPEGRepresentationの引数・返値型を指定する
            func = c.UIImageJPEGRepresentation
            func.argtypes = [ctypes.c_void_p, ctypes.c_float]
            func.restype = ctypes.c_void_p
            # UIImageJPEGRepresentationでJPEGとしてファイル保存
            ui_image_ = ObjCInstance( func(img.ptr, 1.0) )
        elif '.png' == os.path.splitext(file_path)[1].lower():
            # UIImagePNGRepresentationの引数・返値型を指定する
            func = c.UIImagePNGRepresentation
            func.argtypes = [ctypes.c_void_p]
            func.restype = ctypes.c_void_p
            # UIImagePNGRepresentationでPNGとしてファイル保存
            ui_image_ = ObjCInstance( func(img.ptr) )
        ui_image_.writeToFile_atomically_(file_path, True)
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
    picker.sourceType = 0
    # 自分ViewからUIImagePickerControllerを呼ぶ
    #UIApplication = ObjCClass('UIApplication')
    #topController = UIApplication.sharedApplication().keyWindow().rootViewController()
    #while topController.presentedViewController():
    #    topController = topController.presentedViewController()
    #vc = topController
    vc = get_topcontroler()
    vc.presentModalViewController_animated_(picker, True)

# フォトアルバムから静止画を取得する場合
@on_main_thread
def pick_photoalbum_and_save(file_path):
    # 撮影後に呼ばれるdelegateを定義
    def imagePickerController_didFinishPickingMediaWithInfo_(self, cmd, picker, info):
        pick = ObjCInstance(picker)
        pick.setDelegate_(None)  # Set delegate to nil, and release its memory:
        ObjCInstance(self).release()
        pick.dismissViewControllerAnimated_completion_(True, None) # Dismiss the sheet:
        infos = ObjCInstance(info)  # Get UIImage
        #img = infos['UIImagePickerControllerEditedImage']
        img = infos['UIImagePickerControllerOriginalImage']
        if '.jpg' == os.path.splitext(file_path)[1].lower():
            #img.jpegData()
            # UIImageJPEGRepresentationの引数・返値型を指定する
            func = c.UIImageJPEGRepresentation
            func.argtypes = [ctypes.c_void_p, ctypes.c_float]
            func.restype = ctypes.c_void_p
            # UIImageJPEGRepresentationでJPEGとしてファイル保存
            ui_image_ = ObjCInstance( func(img.ptr, 1.0) )
        elif '.png' == os.path.splitext(file_path)[1].lower():
            # UIImagePNGRepresentationの引数・返値型を指定する
            func = c.UIImagePNGRepresentation
            func.argtypes = [ctypes.c_void_p]
            func.restype = ctypes.c_void_p
            # UIImagePNGRepresentationでPNGとしてファイル保存
            ui_image_ = ObjCInstance( func(img.ptr) )
        ui_image_.writeToFile_atomically_(file_path, True)
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
