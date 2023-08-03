
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
def update_image(ui_imageview, image, camera_idx):
    # UIImageViewのimageを更新
    ui_imageview.image = np2ui(image)
    ui_imageview.setNeedsLayout()

# 色画像取得のdelegateから呼ばれる処理関数
def processPixelBuffer( pixelData,
                        sessionPreset,
                        camera_pixFormType,
                        camera_type,
                        camera_idx,
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
        if camera_pixFormType is CV32BGRA:
            _image = np.ctypeslib.as_array(
                ctypes.cast(base_address, ctypes.POINTER(ctypes.c_ubyte)),
                shape=((height, width*4)) )
        else: # YUV_420_888のYだけを取得する場合（条件設定は直しましょう）
            _image = np.ctypeslib.as_array(
                ctypes.cast(base_address, ctypes.POINTER(ctypes.c_ubyte)),
                shape=((height, width)) )
        np_img = copy.copy(_image) # 廃棄防止
    # データ処理用のユーザー関数が与えられていたら
    if user_func is not None and np_img is not None:
        user_func({"type":camera_type, "video":np_img})
    # プレビュー表示用UIViewに対して
    if ui_imageview is not None:
        # 画面表示用のユーザー関数が与えられていたら
        if user_func_ui is not None:
            update_image( ui_imageview,
                          user_func_ui(np_img),
                          camera_idx)
        else:
            update_image( ui_imageview,
            #np_img.reshape(height, width, 4), # 色変換しない場合
            # BGRAからRGBAに変換する
            np_img.reshape(height, width, 4)[:, :, [2,1,0,3]],
            camera_idx)

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
        user_func({"video":video, "depth":depth})
    if ui_imageview is not None:
        # user_func_ui 関数に任せる
        if user_func_ui is not None:
            update_image(ui_imageview,
                user_func_ui({'video':video,'depth':depth}))
        else:
            if pixel_format_type is CV32BGRA:
                update_image(ui_imageview,
                    video.reshape(video_height, video_width, 4))
            else:
                update_image(ui_imageview,
                    video.reshape(video_height, video_width))
    
# -----------------------------------------------------------------------
class AVCaptureVideoCaptureExMulti:
    # コンストラクタ
    def __init__( self,
        captureCameras,       # 取得カメラ群{type, pos, pixFormType}のリスト
        #sessionPreset,         # 取得画像サイズ
        func,                  # 取得画像を使った処理を行うユーザ関数
        func_ui,               # 表示画像を作るユーザ関数
        ui_view ):             # 取得画像を表示するUIView

        # 深度マップ+色の取得を行うか
        self.is_depth_and_color = False
        #if captureDeviceType == 'AVCaptureDeviceTypeBuiltInLiDARDepthCamera' or \
        #   captureDeviceType == 'AVCaptureDeviceTypeBuiltInTrueDepthCamera' or \
        #   captureDeviceType == 'AVCaptureDeviceTypeBuiltInDualWideCamera' or \
        #   captureDeviceType == 'AVCaptureDeviceTypeBuiltInTrueDepthCamera':
        #    self.is_depth_and_color = True
            
        # プロパティの設定
        self.ui_view = ui_view
        self.ui_imageviews = []
        
        self.cameras = captureCameras
        #self.sessionPreset = sessionPreset # 使ってない
        self.user_func = func
        self.user_func_ui = func_ui
        self.devices = []
        self.deviceInputs = []
        self.videoOutputs = []
        self.connections = []
        self.delegates = []
        self.processed_frames = []
        self.epoch_times = []
        self.presets = []
        
        # デバイスを探す（この部分は通常カメラでも特殊カメラでも変わらない）
        #captureDeviceDiscoverySession = AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
        #        [self.captureDeviceType], AVMediaTypeVideo, self.captureDevicePosition)
        #captureDevices = captureDeviceDiscoverySession.devices()
        # デバイスを開く
        #self.device = captureDevices[0] # 該当する最初のデバイスを選択
        
        # キャプチャデバイスから”input”を作る
        #_deviceInput = AVCaptureDeviceInput.deviceInputWithDevice_error_(self.device, None)
        # deviceInputを保持＆セッションに追加する
        
        #if _deviceInput:
        #    self.deviceInput =  _deviceInput
        #    self.session = AVCaptureSession.alloc().init()
        #    # AVCaptureMultiCamSession に変える：A12以降のCPUが必要
        #    self.session = AVCaptureMultiCamSession.alloc().init()
        #
        #    # デバイス追加、本当は session.beginConfigurationとsession.commitConfiguration の間でやる必要がある？
        #    self.session.addInput_(self.deviceInput)
        #else:
        #    return
    
        # デバイス設定をロック（必要であれば）
        # AVCaptureDeviceのactiveFormatに設定するのであれば、この間で設定
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
                synchronizedDataCollection_ = ObjCInstance(_synchronizedDataCollection_)
                syncedVideoData = synchronizedDataCollection_.synchronizedDataForCaptureOutput_(self.videoOutput)
                syncedDepthData = synchronizedDataCollection_.synchronizedDataForCaptureOutput_(self.depthOutput)
                if syncedVideoData and syncedDepthData:
                    sampleBuffer_ = ObjCInstance(ObjCInstance(syncedVideoData).sampleBuffer())
                    # video
                    pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer_)
                    # depth
                    cameraCalibrationData = syncedDepthData.depthData().cameraCalibrationData()
                    depthData = ObjCInstance(syncedDepthData.depthData().depthDataMap())
                    # バッファを取得→ロック＆アクセス→アンロック
                    CVPixelBufferLockBaseAddress(pixelBuffer, 0)   # ロック
                    CVPixelBufferLockBaseAddress(depthData, 0)
                    processPixelAndDepth( pixelBuffer,
                                          depthData,
                                          None, #self.sessionPreset,
                                          self.pixel_format_type,
                                          self.user_func,
                                          self.user_func_ui,
                                          self.ui_imageview)
                    CVPixelBufferUnlockBaseAddress(pixelBuffer, 0)   # アンロック
                    CVPixelBufferUnlockBaseAddress(depthData, 0)
                    self.processed_frames = self.processed_frames + 1 # 枚数更新
            # AVCaptureDataOutputSynchronizerDelegate用ObjCClassを作成する
            DataOutputSynchronizerDelegate = create_objc_class(
                'DataOutputSynchronizerDelegate',
                methods=[dataOutputSynchronizer_didOutputSynchronizedDataCollection_],
                protocols=['AVCaptureDataOutputSynchronizerDelegate'])
                    
        else:
            def captureOutput_didOutputSampleBuffer_fromConnection_(
                  _self, _cmd, _output, # output元が何かがわかる
                  _sample_buffer, _conn):
                  
                _camera_type = None
                _camera_pixFormType = None
                _camera_idx = None
                _output = ObjCInstance(_output)
                # output元を判定する
                for idx, camera in enumerate(self.cameras):
                    if _output == self.videoOutputs[idx]:
                        _camera_type = camera['type']
                        _camera_pixFormType = camera['pixFormType']
                        _camera_idx = idx
                        break
                # iOSのフレームレート設定が面倒なので、手抜き実装
                if time.time() - self.epoch_times[idx] > self.frame_duration:
                    # ピクセルバッファを取得→ロック＆アクセス→アンロック
                    _imageBuffer = CMSampleBufferGetImageBuffer(_sample_buffer)
                    CVPixelBufferLockBaseAddress(_imageBuffer, 0)
                    # 取得情報を使った処理をする
                    processPixelBuffer( _imageBuffer,
                                        None, #self.sessionPreset,
                                        _camera_pixFormType,
                                        _camera_type,
                                        _camera_idx,
                                        self.user_func,
                                        self.user_func_ui,
                                        self.ui_imageviews[idx])
                    CVPixelBufferUnlockBaseAddress(_imageBuffer, 0)
                    self.processed_frames[idx] = self.processed_frames[idx] + 1 # 枚数更新
                    # 時間を更新
                    self.epoch_times[idx] = time.time()
                    
            # AVCaptureVideoDataOutputSampleBufferDelegate用ObjCClassを作成する
            VideoDataOutputSampleBufferDelegate = create_objc_class(
                'VideoDataOutputSampleBufferDelegate', # クラス名
                methods=[captureOutput_didOutputSampleBuffer_fromConnection_],
                protocols=['AVCaptureVideoDataOutputSampleBufferDelegate'])

        # ..... クラス変数を使ったクロージャで、delegate を書く(ここまで) .....

        # queueを作る
        self.queue = ObjCInstance(dispatch_get_current_queue())
        # sessionを追加する
        if AVCaptureMultiCamSession.multiCamSupported:
            self.session = AVCaptureMultiCamSession.alloc().init()
            print('MultiCam is Supported.')
        else:
            self.session = AVCaptureSession.alloc().init()
            print('MultiCam is un-Supported.')
            exit()

        # https://developer.apple.com/documentation/avfoundation/avcapturemulticamsession?language=objc
        # AVCaptureMultiCamSessionでは、sessionPresetは使えない
        # 設定したいのであれば、AVCaptureDeviceのactiveFormatに設定する
        self.session.beginConfiguration()
        for camera in self.cameras:
            # デバイスを探す（この部分は通常カメラでも特殊カメラでも変わらない）
            captureDeviceDiscoverySession = AVCaptureDeviceDiscoverySession.discoverySessionWithDeviceTypes_mediaType_position_(
                [camera['type']], AVMediaTypeVideo, camera['pos'])
            captureDevices = captureDeviceDiscoverySession.devices()
            # デバイスを開く
            _device = captureDevices[0]
                        
            # inputを作り、sessionに追加
            _deviceInput = AVCaptureDeviceInput.deviceInputWithDevice_error_(_device, None)
            
        
            if self.session.canAddInput(_deviceInput):
                #self.session.addInput_(_deviceInput)
                self.session.addInputWithNoConnections_(_deviceInput)
                
                # output(AVCaptureVideoDataOutput)を作り、sessionに追加
                _videoOutput = AVCaptureVideoDataOutput.alloc().init()
                # delegate の処理中に撮影されたフレームは廃棄する
                _videoOutput.alwaysDiscardsLateVideoFrames = True
            
                # ピクセルフォーマットを指定
                if camera['pixFormType'] is not None:
                    _videoOutput.videoSettings = {kCVPixelBufferPixelFormatTypeKey:camera['pixFormType']}
                
                # ここら辺でdelegate設定
                if self.is_depth_and_color: # AVCaptureDataOutputSynchronizerDelegate
                    pass
                    # シンクロナイザを作る
                    #self.depthOutput = AVCaptureDepthDataOutput.alloc().init()
                    #self.session.addOutput_(self.depthOutput)
                    #self.outputVideoSync = AVCaptureDataOutputSynchronizer.alloc()#.init()
                    #self.outputVideoSync.initWithDataOutputs_([self.videoOutput,self.depthOutput])
                    # delegateを作り・設定する
                    #self.delegate = DataOutputSynchronizerDelegate.new()
                    #self.outputVideoSync.setDelegate_queue_(self.delegate, self.queue)
                else:
                    # delegateを作り・設定する
                    _delegate = VideoDataOutputSampleBufferDelegate.new()
                    _videoOutput.setSampleBufferDelegate_queue_(_delegate, self.queue)
                    
                # sessionにoutputを追加
                if self.session.canAddOutput(_videoOutput):
                    self.session.addOutputWithNoConnections(_videoOutput)
                    
                    # 向きも設定しておく (動かない)
                    #videoConnection = _videoOutput.connectionWithMediaType(AVMediaTypeVideo)
                    #videoConnection.videoOrientation = AVCaptureVideoOrientationPortrait
                    
                    # device設定開始
                    _device.lockForConfiguration_(None)
                    # 解像度などの設定
                    if camera['format']  is not None:
                        for idx, format in enumerate(_device.formats()):
                            format_str = "{}".format(format)
                            if "multicam" in format_str:
                                if "high photo quality" in format_str:
                                    if camera['format'] in format_str:
                                        _device.activeFormat = format
                                        break
                    # 撮影フレームレートを設定する(sessionに追加後)
                    # 必要に応じてこの設定をする
                    #### _device.activeVideoMinFrameDuration = CMTime( 1, 10, 1, 0 ) # 1/10
                    #_device.setActiveVideoMinFrameDuration_(CMTime( 50, 100, 1, 0 ), restype=None, argtypes=[CMTime])
                    #_device.setActiveVideoMaxFrameDuration_(CMTime( 50, 100, 1, 0 ), restype=None, argtypes=[CMTime])
                    _device.unlockForConfiguration()

                    # inputとoutputを接続
                    _port = _deviceInput.portsWithMediaType_sourceDeviceType_sourceDevicePosition_(
                                AVMediaTypeVideo, camera['type'], camera['pos'])
                    _connection = AVCaptureConnection.connectionWithInputPorts_output_(_port, _videoOutput)
                    #_connection.videoOrientation = AVCaptureVideoOrientationLandscapeRight
                    
                    if self.session.canAddConnection(_connection):
                        self.session.addConnection(_connection)
                                                
                        # 保持しておく
                        self.devices.append(_device)
                        self.deviceInputs.append(_deviceInput)
                        self.videoOutputs.append(_videoOutput)
                        self.connections.append(_connection)
                        self.delegates.append(_delegate)
                        self.epoch_times.append(0)
                        self.processed_frames.append(0.0)
                        self.ui_imageviews.append(UIImageView.alloc().init())
                        
        self.session.commitConfiguration()

    def add_view(self):
        # 表示用のui_viewを追加
        self.main_view = get_view_controllers()[1].view()
        add_uiview_to_mainview(self.ui_view, self.main_view)
        # UIImageViewをui_viewに追加しておく
        size = self.ui_view.bounds().size
        for idx, camera in enumerate(self.cameras):
            x = idx % 2
            y = 0 if idx <2 else 1
            add_uiview_to_mainview(self.ui_imageviews[idx], self.ui_view)
            rect = CGRect( CGPoint(size.width/2*x, size.height/2*y),
                           CGSize(size.width/2,    size.height/2))
            self.ui_imageviews[idx].frame = rect
            print(self.ui_imageviews[idx].frame)
        
    # カメラ撮影をスタートさせる
    @on_main_thread
    def video_shooting_start(self, frameDuration):
        self.add_view()
        self.frame_duration = frameDuration
        self.session.startRunning()
        self.processed_frame = 0
        for idx, camera in enumerate(self.cameras):
            self.epoch_times[idx] = time.time()

    # カメラ撮影を終了させる
    @on_main_thread
    def video_shooting_close(self, ui_view):
        self.session.stopRunning()
        #self.delegate.release()
        self.session.release()
        
        for videoOutput in self.videoOutputs:
            videoOutput.release()
        
        if self.is_depth_and_color:
            pass
            #self.depthOutput.release()
        
        # プレビューレイヤーを消す（Noneにはしない）
        remove_uiview_fromsuper(ui_view)
