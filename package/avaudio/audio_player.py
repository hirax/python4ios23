import rubicon.objc
import ctypes

#from os.path import abspath

#from ctypes import cdll, c_int, byref
#from avfaudio.sound import *
#import os

AudioToolbox = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/AudioToolbox.framework/AudioToolbox")
AVFoundation = ctypes.cdll.LoadLibrary(
        "/System/Library/Frameworks/AVFoundation.framework/AVFoundation")
AVAudioPlayer = rubicon.objc.ObjCClass("AVAudioPlayer")
NSURL = rubicon.objc.ObjCClass("NSURL")

def av_audio_player_init_with_contents_of_url(url):
    return  AVAudioPlayer.alloc().initWithContentsOfURL(
             url, error = None)
