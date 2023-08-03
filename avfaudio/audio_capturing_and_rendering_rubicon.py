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
AVAudioSourceNode = rubicon_api.ObjCClass('AVAudioSourceNode')

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
'''

kVariableLengthArray = 1  # kVariableLengthArray のこと（interleaved ならステレオでも1のまま）
# AudioBuffer: 音声データを格納するバッファー（構造体）
class AudioBuffer( ctypes.Structure ):
    _fields_ = [
        ('mNumberChannels', ctypes.c_uint32), # チャンネル数 # ステレオなら2
        ('mDataByteSize', ctypes.c_uint32),   # mData領域のサイズ # ステレオInterleavedだと×2
        ('mData', ctypes.c_void_p),           # 音声データ        # ステレオInterleavedだと×2
    ]

# AudioBufferList: AudioBuffer のリスト
class AudioBufferList( ctypes.Structure ):
    _fields_ = [
        ('mNumberBuffers', ctypes.c_uint32), # AudioBufferの配列数
        ('mBuffers', AudioBuffer * kVariableLengthArray), # AudioBufferの配列 # non-interleavedでは対応してない
    ]
  
'''
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

# 音声波形生成関数の例
def rendering_function(t, channel): # channel→0(右)、1(左)
    if channel == 0:
        return 1.0 * math.sin(440.0 * 2.0 * math.pi * t)
    else:
        return 1.0 * math.sin(660.0 * 2.0 * math.pi * t)

# ------------------------------
class AVAudio_Capture_and_Rendering:

    # コンストラクタ
    def __init__( self,
                  buffer_size,              # 音声取得を行う際のバッファーサイズ
                  user_capture_function,    # 取得用関数(処理不要ならNoneをわたす)
                  user_rendering_function,  # 出力用関数（処理不要ならNoneをわたす）
                  channels_for_rendering    # 出力処理のチャンネル数(1=モノラル, 2=ステレオ)
                ):
    
        # 経過時間（スタート時に再度リセットする）
        self.time = 0.0
        # 音声取得を行う際のバッファーサイズを設定
        self.buffer_size = buffer_size
        # リアルタイムに取得した音声データに対して、何かの処理をするための「ユーザー関数」
        self.user_capture_function = user_capture_function
        # リアルタイムに音声データを生成する「ユーザー関数」
        self.user_rendering_function = user_rendering_function
        # 出力チャンネル数
        self.channels = channels_for_rendering
        # 音声の再生・録音ができるモードで、AVAudioEngineを作る
        error = rubicon_api.objc_id(0)
        session = AVAudioSession.sharedInstance()
        category = session.setCategory(
                   'AVAudioSessionCategoryPlayAndRecord',
                   error = ctypes.pointer(error) )
        if error:
            raise Exception('error setting up category')
        # セッションをアクティブにする
        session.setActive( True, error=ctypes.pointer(error) )
        if error:
            raise Exception( 'error setting up session active' )
            
        # AVAudioEngine を作成
        self.AVAudioEngine = AVAudioEngine.new()

        # ---------- マイク入力を音声取得する場合（ここから） ------------
        if user_capture_function is not None:
            # 音声キャプチャ処理をするBlocks用関数を
            # buffer_sizeやuser_capture_functionを使ったクロージャとして定義
            # 実行スレッドはメインスレッドとは限らない
            def capture_block_function(                   # AVAudioNodeTapBlock
                      buffer: ctypes.c_void_p,            # AVAudioPCMBuffer
                      when:   ctypes.c_void_p ) -> None:  # AVAudioTime
                try:
                    # AVAudioPCMBuffer を取得
                    audio_in_buf = rubicon_api.ObjCInstance(buffer)
                    # AVAudioPCMBufferの値をnumpyアレイとして読み込む
                    nparray_audio = np.ctypeslib.as_array(
                        audio_in_buf.floatChannelData[0],
                        (buffer_size, 1) )     # buffer_sizeの1次元リストで受け取る(2次元にはしない)
                    # 音声データをユーザー関数に受け渡す
                    self.user_capture_function(nparray_audio)
                except:
                    raise
            # AudioEngineの暗黙入力ノード(inputNode)はマイク入力
            input_node = self.AVAudioEngine.inputNode
            try:    # マイク入力にタップを付けて音声データをキャプチャする
                input_node.installTapOnBus_bufferSize_format_block_(
                    0,                                 # inputNode(index:0)の出力バスにタップ
                    buffer_size,                       # バッファーサイズ:AVAudioFrameCount
                    input_node.outputFormatForBus_(0), # 出力フォーマットを指定:AVAudioFormat
                                                       # この例(設定そのまま)では、Noneを指定しても良い
                    capture_block_function )           # 呼び出される関数 (AVAudioNodeTapBlock)
            except:
                print('Can not install AVAudioNodeTapBlock.')
                raise
        # ---------- マイク入力を音声取得する場合（ここまで） ------------

        # ---------- 音声出力する場合（ここから） ------------
        if (user_rendering_function is not None) and (channels_for_rendering is not None):
            # 暗黙の出力ノード（デフォルト出力）
            #output_node = self.AVAudioEngine.outputNode
            # 暗黙のMixerノード (デフォルトで暗黙出力ノードは繋がれている)
            mixer_node = self.AVAudioEngine.mainMixerNode
            
            # ★
            #print(mixer_node.numberOfInputs)
            
            # 出力側にとって（入力として）必要な音声フォーマット
            # format_for_output_node = output_node.inputFormatForBus(0) # これでも動く
            format_for_output_node = mixer_node.inputFormatForBus(0)    # これでも動く
        
            self.sampleRate = format_for_output_node.sampleRate
            self.delta_time = 1 / self.sampleRate
            # 出力フォーマットを作る
            format_for_output = AVAudioFormat.alloc().initWithCommonFormat_sampleRate_channels_interleaved_(
                format_for_output_node.commonFormat, self.sampleRate,
                1,  # ひとつのソースノードに対してはチャンネル数=1としておく
                format_for_output_node.isInterleaved )
            self.source_nodes = []           # 音声生成用のノードを格納する
            #self.render_block_functions = [] # 音声生成処理用Blockを格納する
            
            # ......チャンネル番号を受け取り音声生成(Blockから呼ばれる)......
            def render_block_function_with_channel(
                    is_silence, timestamp, frame_count, buffer_p,
                    channel):  # channel→0(右)、1(左)
                
                # 出力用バッファ（AudioBufferList）
                audio_buffer_list = ctypes.cast( buffer_p,
                        ctypes.POINTER(AudioBufferList) ).contents
                # 要求フレーム数分のデータを作る:長さ方向
                t = self.time
                for frame in range(frame_count):
                    # 外部関数で値設定
                    val = user_rendering_function(t, channel=channel)
                    t += self.delta_time
                    for i in range( audio_buffer_list.mNumberBuffers ): # バッファに書き込む
                        # 「各Bufferごと丸っとまとめたサイズ」でcastして、所定アドレスに飛ぶ（ワイルドだ）
                        mData = audio_buffer_list.mBuffers[i].mData
                        pointer = ctypes.POINTER( ctypes.c_float * frame_count )
                        buffer = ctypes.cast( mData, pointer ).contents
                        buffer[frame] = val     # 値を設定する
                if channel == 0:  # 時間を進ませる(2重処理を防ぐ）
                    self.time += self.delta_time * frame_count

            # ...........音声出力用の AVAudioSourceNodeRenderBlock を作る...........
            def render_block_function_0(
                    is_silence: ctypes.c_void_p,           # Boolean
                    timestamp:  ctypes.c_void_p,           # HAL time
                    frame_count: ctypes.c_void_p,          # エンジンが要求したフレーム数
                    buffer_p:   ctypes.c_void_p ) -> None: # ctypes.POINTER(AudioBufferList)では自動型変換できない
                # ........ 処理の実体を呼ぶ ........
                render_block_function_with_channel(
                    is_silence, timestamp, frame_count, buffer_p, 0)
            
            # ...........音声出力用の AVAudioSourceNodeRenderBlock を作る...........
            def render_block_function_1(
                    is_silence: ctypes.c_void_p,           # Boolean
                    timestamp:  ctypes.c_void_p,           # HAL time
                    frame_count: ctypes.c_void_p,          # エンジンが要求したフレーム数
                    buffer_p:   ctypes.c_void_p ) -> None: # ctypes.POINTER(AudioBufferList)では自動型変換できない
                # ........  処理の実体を呼ぶ ........
                render_block_function_with_channel(
                    is_silence, timestamp, frame_count, buffer_p, 1)
            
            # .........チャンネルごとにAVAudioSourceNodeRenderBlockを設定する.......
            for channel in range(self.channels):
                print(channel)
                # sourcenodeを作る
                #self.source_nodes.append( AVAudioSourceNode.alloc() )
                src = AVAudioSourceNode.alloc()
                #src.init()
                #src.init()
                self.source_nodes.append( src )

                # ★
                #print(src.numberOfOutputs)

                # ソースノード処理としてAVAudioSourceNodeRenderBlockを登録する（デフォルト引数のみ違う）
                #self.source_nodes[channel].initWithFormat_renderBlock_( # ★
                #    format_for_output,         # AVAudioFormat
                #    render_block_function )    # AVAudioSourceNodeRenderBlock ここで"render_block_function"が上書きされる？
                
                if channel == 0: # 右
                    func = render_block_function_0
                if channel == 1: # 左
                    func = render_block_function_1
                # sourece nodeをrenderBlockで初期化
                self.source_nodes[channel].initWithFormat_renderBlock_( format_for_output, func )
                # source nodeをAVAudioEngineに追加
                self.AVAudioEngine.attachNode( self.source_nodes[channel] )
                
                # 暗黙のミキサーに接続する
                #self.AVAudioEngine.connect_to_format_(self.source_nodes[channel],
                #mixer_node, format_for_output)  # mixer_node に繋ぐ(mixer_node.inputFormatForBus(0)でもOK)
                # 暗黙のミキサーに接続する
                self.AVAudioEngine.connect_to_fromBus_toBus_format_(
                        self.source_nodes[channel],
                        mixer_node,
                        0, channel,
                        format_for_output)  # mixer_node に繋ぐ(mixer_node.inputFormatForBus(0)でもOK)
                    #None)  # mixer_node に繋ぐ(mixer_node.inputFormatForBus(0)でもOK)

            # 暗黙のミキサーと出力はデフォルトで繋がれている
            #self.AVAudioEngine.connect_to_format_(mixer_node, output_node, format_for_output)
        # ---------- 音声出力する場合（ここまで） ------------


    # 音声処理をするための準備動作をさせる
    def prepare(self):
        self.AVAudioEngine.prepare()
    
    # 音声処理を開始する
    def start(self):
        self.AVAudioEngine.startAndReturnError(None)
        self.time = 0.0 # 経過時間をリセット
        # ステレオ時には定位を設定する( AVAudioEngine.start 後に実行が必要)
        if self.channels == 2:
            self.source_nodes[0].pan =  1 # right
            self.source_nodes[1].pan = -1 # left
        #self.AVAudioEngine.mainMixerNode.outputVolume = 1.0
    
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
def capturte_block_function(
                  buffer: ctypes.c_void_p,            # AVAudioPCMBuffer
                  when:   ctypes.c_void_p ) -> None:  # AVAudioTime
    try:
        # AVAudioPCMBuffer
        audio_in_buf = rubicon_api.ObjCInstance(buffer)
        # AVAudioPCMBufferの値をnumpyアレイとして読み込む
        A = np.ctypeslib.as_array(
              # AVAudioPCMBuffer * で渡されるので[0]つける
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

