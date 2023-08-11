# coding: utf-8
# Copyright (c) 2018 Jun Hirabayashi (jun@hirax.net)
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php

# from iOS03

from classes.header import *
import rubicon.objc
import time
import os

# クラスへのリファレンスを作る
try:
    AVAudioSession  = rubicon.objc.api.ObjCClass('AVAudioSession')
    AVAudioRecorder = rubicon.objc.api.ObjCClass('AVAudioRecorder')
    NSURL           = rubicon.objc.api.ObjCClass('NSURL')
except NameError:
    print('error: Class not found.')

# ファイルに録音する
def avaudio_recorder_record( file_name = "record.wav", duration=3,
                             AVFormatIDKey = AVFormatIDKey.kAudioFormatLinearPCM,
                             AVSampleRateKey = 44100.00,
                             AVNumberOfChannelsKey = 2,
                             AVEncoderAudioQualityKey = AVAudioQuality.AVAudioQualityMedium ):
    record_file_url = NSURL.fileURLWithPath_( os.path.abspath( file_name ) )
    shared_avaudio_session = AVAudioSession.sharedInstance()
    category_set = shared_avaudio_session.setCategory_error_( 'AVAudioSessionCategoryPlayAndRecord', None )
    settings = {'AVFormatIDKey': AVFormatIDKey.kAudioFormatLinearPCM,
                'AVSampleRateKey': 44100.00,
                'AVNumberOfChannelsKey': 2,
                'AVEncoderAudioQualityKey': AVAudioQuality.AVAudioQualityMedium
    }
    
    AVAudioRecorder_ = AVAudioRecorder.alloc().initWithURL_settings_error_(
                         record_file_url, settings, None )
    started_recording = AVAudioRecorder_.record()
    time.sleep(duration)
    AVAudioRecorder_.stop()
    AVAudioRecorder_.release()
    
if __name__ == '__main__':
    avaudio_recorder_record( file_name = "record.wav", duration = 3 )
    
