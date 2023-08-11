
import ctypes
from objc_util import *
import numpy as np
import copy
from uikit.ui_uiview import *
from uikit.ui_uiimage_convert import *
import time

from defines import *

# フレームワーク読み込み
AVFoundation = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/AVFoundation.framework/AVFoundation"
)

# 処理した画像を画面に表示させるための関数
@on_main_thread
def update_image(ui_imageview, image):
    # UIImageViewのimageを更新
    ui_imageview.image = np2ui(image)
    ui_imageview.setNeedsLayout()

# 色画像取得のdelegateから呼ばれる処理関数
def processPixelBuffer( pixelData,
                        sessionPreset,
                        pixel_format_type,
                        user_func,
                        user_func_ui,
                        ui_imageview ):
    width = CVPixelBufferGetWidthOfPlane(pixelData, 0)
    height = CVPixelBufferGetHeightOfPlane(pixelData, 0)
    base_address  = CVPixelBufferGetBaseAddressOfPlane(pixelData, 0)
    bytes_per_row = CVPixelBufferGetBytesPerRowOfPlane(pixelData, 0)
    if base_address is None: # バッファ取得できなければ、飛ばす
        return
    if (user_func is not None) or (ui_imageview is not None):
        if pixel_format_type is CV32BGRA:
            _image = np.ctypeslib.as_array(
                ctypes.cast(base_address, ctypes.POINTER(ctypes.c_ubyte)),
                shape=((height, width*4)) )
        else: # YUV_420_888のYだけを取得する場合（条件設定は直しましょう）
            _image = np.ctypeslib.as_array(
                ctypes.cast(base_address, ctypes.POINTER(ctypes.c_ubyte)),
                shape=((height, width)) )
        np_img = copy.copy(_image) # 廃棄防止
    # データ処理用のユーザー関数が与えられていたら
    if user_func is not None:
        user_func({"video":np_img})
    # プレビュー表示用UIViewに対して
    if ui_imageview is not None:
        # 画面表示用のユーザー関数が与えられていたら
        if user_func_ui is not None:
            update_image(ui_imageview, user_func_ui(np_img))
        # 画面表示をデフォルト処理する
        else:
            update_image( ui_imageview,
            #np_img.reshape(height, width, 4) # 色変換しない場合
            # BGRAからRGBAに変換する
            np_img.reshape(height,width,4)[:,:,[2,1,0,3]]
            )
            
# 色画像と距離画像取得のdelegateから呼ばれる処理関数
def processPixelAndDepth( pixelBuffer,
                          depthData,
                          sessionPreset,
                          pixel_format_type,
                          user_func,
                          user_func_ui,
                          ui_imageview):
    # video
    video_width = CVPixelBufferGetWidthOfPlane(pixelBuffer,0)
    video_height = CVPixelBufferGetHeightOfPlane(pixelBuffer,0)
    video_base_address = CVPixelBufferGetBaseAddressOfPlane(pixelBuffer,0)
    video_bytes_per_row = CVPixelBufferGetBytesPerRowOfPlane(pixelBuffer,0)
    # depth
    depth_width = CVPixelBufferGetWidthOfPlane(depthData,0)
    depth_height = CVPixelBufferGetHeightOfPlane(depthData,0)
    depth_base_address = CVPixelBufferGetBaseAddressOfPlane(depthData,0)
    depth_bytes_per_row = CVPixelBufferGetBytesPerRowOfPlane(depthData,0)
    
    if video_base_address is None or depth_base_address is None:
        return  # バッファ取得できなければ、飛ばす
    if (user_func is not None) or (ui_imageview is not None):
        if pixel_format_type is CV32BGRA:
            video = np.ctypeslib.as_array(
                ctypes.cast(video_base_address, ctypes.POINTER(ctypes.c_ubyte)),
                shape=((video_height, video_width*4)) )
        else: # YUV_420_888のYだけを取得する場合（条件設定は直しましょう）
            video = np.ctypeslib.as_array(
                ctypes.cast(video_base_address, ctypes.POINTER(ctypes.c_ubyte)),
                shape=((video_height, video_width)) )
        depth = np.ctypeslib.as_array(
            ctypes.cast(depth_base_address, ctypes.POINTER(ctypes.c_uint16)),
            shape=( (depth_height, depth_width) ))
    if user_func is not None:
        # データ破棄防止にコピーする
        user_func({"video":copy.copy(video), "depth":copy.copy(depth)})
    if ui_imageview is not None:
        # 画面表示用のユーザー関数が与えられていたら
        if user_func_ui is not None:
            update_image(ui_imageview, user_func_ui({'video':video,'depth':depth}))
        # 画面表示をデフォルト処理する
        else:
            if pixel_format_type is CV32BGRA:
                update_image(ui_imageview,
                    #video.reshape(video_height, video_width, 4) # 色変換しない場合
                    # BGRAからRGBAに変換する
                    video.reshape(video_height,video_width,4)[:,:,[2,1,0,3]]
                    )
            else:
                update_image(ui_imageview,
                    video.reshape(video_height, video_width))
    
# -----------------------------------------------------------------------
class AVCaptureVideoCaptureEx:
    # コンストラクタ
    def __init__( self,
        captureDeviceType,     # 取得デバイス:
        captureDevicePosition, # 取得デバイス位置
        sessionPreset,         # 取得画像サイズ
        pixel_format_type,     # 画像色フォーマット
        func,                  # 取得画像を使った処理を行うユーザ関数
        func_ui,               # 表示画像を作るユーザ関数
        ui_view ):             # 取得画像を表示するUIView

        # プロパティの設定
        self.ui_view = ui_view
        self.captureDeviceType = captureDeviceType
        self.captureDevicePosition = captureDevicePosition
        self.sessionPreset = sessionPreset
        self.pixel_format_type = pixel_format_type
        self.user_func = func
        self.user_func_ui = func_ui
        self.processed_frames = None
        self.is_depth_and_color = False

        # 深度マップ+色の取得を行うか
        if captureDeviceType == 'AVCaptureDeviceTypeBuiltInLiDARDepthCamera' or \
           captureDeviceType == 'AVCaptureDeviceTypeBuiltInTrueDepthCamera' or \
           captureDeviceType == 'AVCaptureDeviceTypeBuiltInDualWideCamera' or \
           captureDeviceType == 'AVCaptureDeviceTypeBuiltInTrueDepthCamera':
            self.is_depth_and_color = True
        
        # デバイスを探す（この部分は通常カメラでも特殊カメラでも変わらない）
        captureDeviceDiscoverySession = AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
                [self.captureDeviceType], AVMediaTypeVideo, self.captureDevicePosition)
        captureDevices = captureDeviceDiscoverySession.devices()
        # デバイスを開く
        self.device = captureDevices[0] # 該当する最初のデバイスを選択
        # キャプチャデバイスから”input”を作る
        _deviceInput = AVCaptureDeviceInput.deviceInputWithDevice_error_(self.device, None)
        # deviceInputを保持＆セッションに追加する
        if _deviceInput:
            self.deviceInput =  _deviceInput
            # sessionを作成
            self.session = AVCaptureSession.alloc().init()
            
            # deviceをsessionに追加
            # デバイス追加、本当は session.beginConfigurationとsession.commitConfiguration の間でやる必要がある？
            self.session.addInput_(self.deviceInput)
        else:
            return
    
        # デバイス設定をロック（必要であれば）
        #self.device.lockForConfiguration_(None)
        # フォーカス設定
        #self.device.focusMode = AVCaptureFocusModeLocked
        #self.device.setFocusModeLockedWithLensPosition_completionHandler_( 0.5, None )
        # デバイス設定をアンロック
        #self.device.unlockForConfiguration()

        # ..... クラス変数を使ったクロージャで、delegate を書く .....
        if self.is_depth_and_color:
            def dataOutputSynchronizer_didOutputSynchronizedDataCollection_(
                 _self, _cmd, _synchronizer_, _synchronizedDataCollection_):
                # # 色画像と距離マップ画像を同期させるための準備
                synchronizedDataCollection_ = ObjCInstance(_synchronizedDataCollection_)
                syncedVideoData = synchronizedDataCollection_.synchronizedDataForCaptureOutput_(self.videoOutput)
                syncedDepthData = synchronizedDataCollection_.synchronizedDataForCaptureOutput_(self.depthOutput)
                if syncedVideoData and syncedDepthData:
                    sampleBuffer_ = ObjCInstance(ObjCInstance(syncedVideoData).sampleBuffer())
                    # 色画像
                    pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer_)
                    # 距離マップ画像
                    cameraCalibrationData = syncedDepthData.depthData().cameraCalibrationData()
                    depthData = ObjCInstance(syncedDepthData.depthData().depthDataMap())
                    # バッファを取得→ロック＆アクセス→アンロック
                    CVPixelBufferLockBaseAddress(pixelBuffer, 0)   # ロック
                    CVPixelBufferLockBaseAddress(depthData, 0)
                    processPixelAndDepth( pixelBuffer,
                                          depthData,
                                          self.sessionPreset,
                                          self.pixel_format_type,
                                          self.user_func,
                                          self.user_func_ui,
                                          self.ui_imageview)
                    CVPixelBufferUnlockBaseAddress(pixelBuffer, 0)   # アンロック
                    CVPixelBufferUnlockBaseAddress(depthData, 0)
                    self.processed_frames = self.processed_frames + 1 # 時間更新
            # AVCaptureDataOutputSynchronizerDelegate用ObjCClassを作成する
            DataOutputSynchronizerDelegate = create_objc_class(
                'DataOutputSynchronizerDelegate',
                methods=[dataOutputSynchronizer_didOutputSynchronizedDataCollection_],
                protocols=['AVCaptureDataOutputSynchronizerDelegate'])
                    
        else:
            def captureOutput_didOutputSampleBuffer_fromConnection_(
                  _self, _cmd, _output, _sample_buffer, _conn):
                # iOSのフレームレート設定が面倒なので、手抜き実装
                if time.time() - self.epoch_time > self.frame_duration:
                    self.epoch_time = time.time()
                    # ピクセルバッファを取得→ロック＆アクセス→アンロック
                    _imageBuffer = CMSampleBufferGetImageBuffer(_sample_buffer)
                    CVPixelBufferLockBaseAddress(_imageBuffer, 0)
                    # 取得情報を使った処理をする
                    processPixelBuffer( _imageBuffer,
                                        self.sessionPreset,
                                        self.pixel_format_type,
                                        self.user_func,
                                        self.user_func_ui,
                                        self.ui_imageview)
                    CVPixelBufferUnlockBaseAddress(_imageBuffer, 0)
                    self.processed_frames = self.processed_frames + 1 # 時間更新
                    
            # 作成した関数を使ってdelegate用のクラスを作る
            VideoDataOutputSampleBufferDelegate = create_objc_class(
                'VideoDataOutputSampleBufferDelegate', # クラス名
                methods=[captureOutput_didOutputSampleBuffer_fromConnection_],
                protocols=['AVCaptureVideoDataOutputSampleBufferDelegate'])

        # ..... クラス変数を使ったクロージャで、delegate を書く(ここまで) .....

        # ------ outputを作って・sessionに接続する -------------
        # output(AVCaptureVideoDataOutput)を作成
        self.videoOutput = AVCaptureVideoDataOutput.alloc().init()
        if pixel_format_type is not None:
            self.videoOutput.videoSettings = {
                kCVPixelBufferPixelFormatTypeKey:pixel_format_type }
        # outputをセッションに接続
        self.session.addOutput_(self.videoOutput)
        
        # 向きも設定しておく
        videoConnection = self.videoOutput.connectionWithMediaType(AVMediaTypeVideo)
        videoConnection.videoOrientation = AVCaptureVideoOrientationPortrait
        
        # session設定をする
        self.session.beginConfiguration()
        self.session.sessionPreset = sessionPreset
        self.session.commitConfiguration()
        
        # queueを作る
        self.queue = ObjCInstance(dispatch_get_current_queue())
        
        if self.is_depth_and_color: # AVCaptureDataOutputSynchronizerDelegate
            # シンクロナイザを作る
            self.depthOutput = AVCaptureDepthDataOutput.alloc().init()
            self.session.addOutput_(self.depthOutput)
            
            # 向きも設定しようとしたら、データが狂ったので、後処理で回転させることにする
            #depthConnection = self.depthOutput.connectionWithMediaType(AVMediaTypeDepthData)
            #depthConnection.videoOrientation = AVCaptureVideoOrientationPortrait

            
            self.outputVideoSync = AVCaptureDataOutputSynchronizer.alloc()#.init()
            self.outputVideoSync.initWithDataOutputs_([
                self.videoOutput,
                self.depthOutput])
            # delegateを作り・設定する
            self.delegate = DataOutputSynchronizerDelegate.new()
            self.outputVideoSync.setDelegate_queue_(self.delegate, self.queue)
        else:                  # AVCaptureVideoDataOutputSampleBufferDelegate
            # delegateを作り・設定する
            self.delegate = VideoDataOutputSampleBufferDelegate.new()
            self.videoOutput.setSampleBufferDelegate_queue_(self.delegate, self.queue)
        # delegate の処理中に撮影されたフレームは廃棄する
        self.videoOutput.alwaysDiscardsLateVideoFrames = True

    def add_view(self):
        # 表示用のui_viewを追加
        self.main_view = get_view_controllers()[1].view()
        add_uiview_to_mainview(self.ui_view, self.main_view)
        # UIImageViewをui_viewに追加しておく
        self.ui_imageview = UIImageView.alloc().init()
        self.ui_imageview.frame = self.ui_view.bounds()
        add_uiview_to_mainview(self.ui_imageview, self.ui_view)
    
    # カメラ撮影をスタートさせる
    @on_main_thread
    def video_shooting_start(self, frameDuration):
        self.add_view()
        self.epoch_time = time.time()
        self.frame_duration = frameDuration
        self.session.startRunning()
        self.processed_frames = 0

    # カメラ撮影を終了させる
    @on_main_thread
    def video_shooting_close(self, ui_view):
        self.session.stopRunning()
        #self.delegate.release()
        self.session.release()
        self.videoOutput.release()
        if self.is_depth_and_color:
            self.depthOutput.release()
        
        # プレビューレイヤーを消す（Noneにはしない）
        remove_uiview_fromsuper(ui_view)
        print( "processed_frames:{}".format(self.processed_frames))
