# coding: utf-8
# Copyright (c) 2018 Jun Hirabayashi (jun@hirax.net)
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php

import rubicon.objc
#import rubicon.objc as rubicon.objc

# クラスへのリファレンスを作る
try:
    AVSpeechSynthesizer = rubicon.objc.api.ObjCClass( 'AVSpeechSynthesizer' )
    AVSpeechSynthesisVoice = rubicon.objc.api.ObjCClass( 'AVSpeechSynthesisVoice' )
    AVSpeechUtterance = rubicon.objc.api.ObjCClass( 'AVSpeechUtterance' )
except NameError:
    print('error: Class not found.')

# voice種類を確認する
def speechVoices():
    voices = AVSpeechSynthesisVoice.speechVoices()
    for v in voices:
        print(v)

AVSpeechSynthesizer_ = AVSpeechSynthesizer.new()

# 喋る
def speech( str = "こんにちはPython.", rate = 0.5, volume = 1.0,
           pitchMultiplier = 1.0, preUtteranceDelay = 0.2,
           voice = 'com.apple.ttsbundle.siri_Hattori_ja-JP_compact' ):
    utterance =AVSpeechUtterance.speechUtteranceWithString_( str )
    utterance.voice = AVSpeechSynthesisVoice.voiceWithIdentifier_( voice )
    utterance.rate = rate # 喋る速度
    utterance.volume = volume
    utterance.pitchMultiplier = pitchMultiplier # 声のピッチ
    utterance.preUtteranceDelay = preUtteranceDelay
    utterance.useCompactVoice = False
    AVSpeechSynthesizer_.speakUtterance_( utterance ) # 喋る

if __name__ == '__main__':
    speech(str="こんにちはPython.", rate=0.5, volume = 1.0,
    pitchMultiplier = 1.0, preUtteranceDelay = 0.2,
    voice='com.apple.ttsbundle.siri_Hattori_ja-JP_compact')
