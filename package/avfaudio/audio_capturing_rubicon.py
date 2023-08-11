# https://gist.github.com/jsbain/2cf4998949f49b58ff284239784e1561


from rubicon.objc import api as rubicon_api
import ctypes
import io
import numpy as np
#import time

# フレームワークを読み込む
AVFoundation = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/AVFoundation.framework/AVFoundation"
)
AudioToolbox = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/AudioToolbox.framework/AudioToolbox"
)

# AVAudio 関係のクラスを読み込む
AVAudioEngine = rubicon_api.ObjCClass('AVAudioEngine')
AVAudioSession = rubicon_api.ObjCClass('AVAudioSession')
AVAudioPCMBuffer = rubicon_api.ObjCClass('AVAudioPCMBuffer')
AVAudioFormat = rubicon_api.ObjCClass('AVAudioFormat')

'''
AVAudioPlayerNode = rubicon_api.ObjCClass('AVAudioPlayerNode')
AVAudioFile = rubicon_api.ObjCClass('AVAudioFile')
AVAudioUnitEQ = rubicon_api.ObjCClass('AVAudioUnitEQ')
AVAudioMixerNode = rubicon_api.ObjCClass('AVAudioMixerNode')
AVAudioUnitEQFilterParameters = rubicon_api.ObjCClass('AVAudioUnitEQFilterParameters')
AVAudioSessionPortDescription = rubicon_api.ObjCClass('AVAudioSessionPortDescription')
AVAudioCompressedBuffer = rubicon_api.ObjCClass('AVAudioCompressedBuffer')
AVAudioConverter = rubicon_api.ObjCClass('AVAudioConverter')
AVAudioTime = rubicon_api.ObjCClass('AVAudioTime')

class AudioStreamBasicDescription(ctypes.Structure):
    _fields_=[
    ('mSampleRate',ctypes.c_double),
    ('mFormatID',ctypes.c_uint32),
    ('mFormatFlags',ctypes.c_uint32),
    ('mBytesPerPacket',ctypes.c_uint32),
    ('mFramesPerPacket',ctypes.c_uint32),
    ('mBytesPerFrame',ctypes.c_uint32),
    ('mChannelsPerFrame',ctypes.c_uint32),
    ('mBitsPerChannel',ctypes.c_uint32),
    ('mReserved',ctypes.c_uint32)
    ]
'''

class AVAudioNodeTapBlock_Capture:

    # コンストラクタ
    def __init__( self,
                  buffer_size,
                  user_capture_function
                ):
        # 音声取得を行う際のバッファーサイズを設定
        self.buffer_size = buffer_size
        # リアルタイムに得たデータに処理をさせる「ユーザー関数」
        self.user_capture_function = user_capture_function
        # 音声の再生・録音ができるモードで、AVAudioEngineを作る
        error = rubicon_api.objc_id(0)
        session = AVAudioSession.sharedInstance()
        category = session.setCategory(
                   'AVAudioSessionCategoryPlayAndRecord',
                   error = ctypes.pointer(error)
               )
        if error:
            raise Exception('error setting up category')
        session.setActive( True, error=ctypes.pointer(error) )
        if error:
            raise Exception( 'error setting up session active' )
        self.AVAudioEngine = AVAudioEngine.new()

        # 音声キャプチャ処理をするBlocks用関数を
        # buffer_sizeやuser_functionを使ったクロージャとして定義
        # 実行スレッドはメインスレッドとは限らない
        def capture_block_function(                   # AVAudioNodeTapBlock
                  buffer: ctypes.c_void_p,            # AVAudioPCMBuffer
                  when:   ctypes.c_void_p ) -> None:  # AVAudioTime
            try:
                # AVAudioPCMBuffer を取得
                audio_in_buf = rubicon_api.ObjCInstance(buffer)
                # AVAudioPCMBufferの値をnumpyアレイとして読み込む
                nparray_audio = np.ctypeslib.as_array(
                    # AVAudioPCMBuffer * で渡されるので[0]つける
                    audio_in_buf.floatChannelData[0],
                    (buffer_size,1) )
                # 音声データをユーザー関数に受け渡す
                self.user_capture_function(nparray_audio)
                pass
            except:
                raise
        
        #mixer = self.AVAudioEngine.mainMixerNode
        
        # AudioEngineの暗黙入力ノード(inputNode)は、
        # マイクからの入力。暗黙入力ノードにタップを入れて、
        # 音声データをキャプチャする
        input = self.AVAudioEngine.inputNode
        try:
            input.installTapOnBus_bufferSize_format_block_(
                0,                             # inputNode(index:0)の出力バスにタップ
                buffer_size,                   # バッファーサイズ:AVAudioFrameCount
                input.outputFormatForBus_(0),  # 出力フォーマットを指定:AVAudioFormat
                                               # この例(設定そのまま)では、Noneを指定しても良い
                capture_block_function )       # 呼び出される関数 (AVAudioNodeTapBlock)
            pass
        except:
            print('Can not install AVAudioNodeTapBlock.')
            raise
    
    # 音声処理をするための準備動作をさせる
    def prepare(self):
        self.AVAudioEngine.prepare()
    
    # 音声処理を開始する
    def start(self):
        self.AVAudioEngine.startAndReturnError_(None)
    
    # 音声処理を停止する
    def stop(self):
        self.AVAudioEngine.stop()
    
    # AVAudioEngineをリセットする
    def reset(self):
        AVAudioEngine_.reset()

#######################


AVAudioEngine_ = None
#audio_in_buf = []
#image_convert_bIO = io.BytesIO()
#lastt = 0

BUFFER_SIZE = 4096

# AVAudioEngine を返す
def setup():
    # AVAudioSessionを作成・設定する
    error = rubicon_api.objc_id(0) # Objc_utilならctypes.c_void_p(0)
    session = AVAudioSession.sharedInstance()
    category = session.setCategory(
                   'AVAudioSessionCategoryPlayAndRecord',
                   error = ctypes.pointer(error)
               )
    if error:
        raise Exception('error setting up category')
    session.setActive( True, error=ctypes.pointer(error) )
    if error:
        raise Exception( 'error setting up session active' )
    # AVAudioEngineを作成
    engine = AVAudioEngine.new()
    return engine

# オーディオ処理をするBlocks用関数 (AVAudioNodeTapBlock)
def process_block_function(
                  buffer: ctypes.c_void_p,            # AVAudioPCMBuffer
                  when:   ctypes.c_void_p ) -> None:  # AVAudioTime
    try:
        # AVAudioPCMBuffer
        audio_in_buf = rubicon_api.ObjCInstance(buffer)
        # AVAudioPCMBufferの値をnumpyアレイとして読み込む
        A = np.ctypeslib.as_array(
              audio_in_buf.floatChannelData[0],
              (BUFFER_SIZE,1)
        )
        print(A)
        pass
    except:
        raise

def setup_audio_input_engine():
    global AVAudioEngine_
    # AudioEngine を作成
    AVAudioEngine_ = setup()
    mixer = AVAudioEngine_.mainMixerNode
    input = AVAudioEngine_.inputNode
    try:
        # マイク入力を表す暗黙入力に、AVAudioNodeTapBlockをタップする
        input.installTapOnBus_bufferSize_format_block_(
            0,                             # AVAudioNodeBus
            BUFFER_SIZE,                   # AVAudioFrameCount
            input.outputFormatForBus_(0),  # AVAudioFormat
            process_block_function )       # AVAudioNodeTapBlock
        pass
    except:
        print('Can not install.')
        raise
    AVAudioEngine_.prepare()
    print("Setup is done.")

def start_audio_input_engine():
    global AVAudioEngine_
    AVAudioEngine_.startAndReturnError_(None)

def stop_audio_input_engine():
    global AVAudioEngine_
    AVAudioEngine_.stop()
    AVAudioEngine_.reset()

