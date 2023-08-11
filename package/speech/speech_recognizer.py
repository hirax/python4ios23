from rubicon.objc import api as rubicon_api
import ctypes

# original
# https://forum.omz-software.com/topic/5491/implementing-live-voice-commands/16

# フレームワークを読み込む
AVFoundation = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/AVFoundation.framework/AVFoundation"
)
Speech = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/Speech.framework/Speech"
)

NSLocale = rubicon_api.ObjCClass('NSLocale')
SFSpeechRecognizer = rubicon_api.ObjCClass('SFSpeechRecognizer')
AVAudioEngine = rubicon_api.ObjCClass('AVAudioEngine')
AVAudioSession = rubicon_api.ObjCClass('AVAudioSession')
SFSpeechAudioBufferRecognitionRequest = rubicon_api.ObjCClass('SFSpeechAudioBufferRecognitionRequest')

AVAudioSessionCategoryOptionDuckOthers = 0x2
AVAudioSessionSetActiveOptionNotifyOthersOnDeactivation = 1

class Recognizer:
    
    def __init__(self, _locale_str, isAddsPunctuation):
        locale = NSLocale.alloc().initWithLocaleIdentifier(
              _locale_str) # "ja_JP", "en-US"
        # 認識結果を格納する
        self.result = None
        # SFSpeechRecognizer をインスタンス化
        self.speech_recognizer = SFSpeechRecognizer.alloc().initWithLocale(locale)
        # 音声入力エンジンやノードを作る
        self.audio_engine = AVAudioEngine.new()
        self.input_node = self.audio_engine.inputNode
        self.addsPunctuation = isAddsPunctuation
        self.recognition_request = None
        self.recognition_task = None
        # 音声入力セッションを作る
        self.audio_session = AVAudioSession.sharedInstance()
        self.audio_session.setCategory_mode_options_error_(
            'AVAudioSessionCategoryRecord',
            'AVAudioSessionModeMeasurement',
            AVAudioSessionCategoryOptionDuckOthers, None)
        self.audio_session.setActive_withOptions_error_(True,
            AVAudioSessionSetActiveOptionNotifyOthersOnDeactivation, None)
        # 音声認識を行う設定にする
        self.recognition_request = SFSpeechAudioBufferRecognitionRequest.new()
        # 句読点などの自動認識設定を行う
        self.recognition_request.addsPunctuation = self.addsPunctuation

        if self.recognition_request is None:
            print("Error: could not create recognition request!")
            return
        self.recognition_request.shouldReportPartialResults = True

        # 音声認識時に呼ばれるhandler
        def recognitionTaskWithRequest_resultHandler(
                result_ptr: ctypes.c_void_p,
                error_ptr:  ctypes.c_void_p) -> None:
            is_final = False
            if not result_ptr is None:
                result = rubicon_api.ObjCInstance(result_ptr)
                is_final = result.isFinal
                self.result = str(result.bestTranscription.formattedString)
            if not error_ptr is None:# or is_final:
                if error_ptr is not None:
                    error = rubicon_api.ObjCInstance(error_ptr)
                    print("Error in recognition task:", error)
        # 音声入力から音声認識をさせるblock
        def installTapOnBus_tapBlock(buffer_ptr: ctypes.c_void_p,
                                     when_ptr: ctypes.c_void_p) -> None:
            buffer = rubicon_api.ObjCInstance(buffer_ptr)
            when = rubicon_api.ObjCInstance(when_ptr)
            if not self.recognition_request is None:
                self.recognition_request.appendAudioPCMBuffer_(buffer)
                
        self.recognitionTaskWithRequest_resultHandler = recognitionTaskWithRequest_resultHandler
        self.installTapOnBus_tapBlock = installTapOnBus_tapBlock

    def prepare(self):
        
        if self.recognition_task is not None:
            print("Speech recognition already active.")
            return
        print("Starting speech recognition.")
        # 音声認識のためのblockやhandlerを登録する
        self.recognition_task = self.speech_recognizer.recognitionTaskWithRequest_resultHandler_(
            self.recognition_request,
            self.recognitionTaskWithRequest_resultHandler)
        # 音声認識のためのタップを貼る
        recording_format = self.input_node.outputFormatForBus_(0)
        self.input_node.installTapOnBus_bufferSize_format_block_(0, 1024,
                                        recording_format,
                                        self.installTapOnBus_tapBlock)
        self.audio_engine.prepare()

    def start(self):
        self.audio_engine.startAndReturnError_(None)
    
    def stop(self):
        self.audio_engine.stop()
        self.input_node.removeTapOnBus_(0)
        self.recognition_request = None
        self.recognition_task = None
        if self.audio_engine.isRunning():
            self.audio_engine.stop()
            if self.recognition_request is not None:
                self.recognition_request.endAudio()
                
