# coding: utf-8
# Jun Hirabayashi (jun@hirax.net, twitter @hirax)
# This code is based on Brun0oO's work(MIT License)
# https://github.com/Brun0oO/Pythonista/blob/master/arkit/main.py
# and Charles Surett's work.
# https://github.com/scj643/objc_tools/blob/master/objc_tools/scenekit/sk_scene.py
# Following thread will be heplful for understanding how Pythonista can call ARKit.
# https://forum.omz-software.com/topic/4362/solved-first-attempt-to-integrate-arkit-and-first-questions/29

# info
# https://blog.pusher.com/building-an-ar-app-with-arkit-and-scenekit/
# http://www.cl9.info/entry/2017/10/07/110000

import os, sys, time, math
from enum import IntFlag
from objc_util.objc_util import *
from objc_tools.scenekit.util import SUPPORTED_FORMATS, LightType, ShadowMode, DebugOptions, RenderingAPI, LightingModel # ui 使わず
from objc_tools.scenekit.structures import Vector3, Vector4, Matrix4 # ui 使わず
from objc_tools.ui.editorview import TabView, tabVC # ui 使わず
from defines.defines import *
import numpy as np
from coreimage.core_image import *
from uikit.ui_uiimage_convert import *
import copy

# ------------ SeneKit View -----------------
class SKView (object):
    '''SKView
        This object is used for subclassing
    '''
    def __init__(self):
        self._create_objc()
        self.attach()
    
    def _create_objc(self):
        self._scene_objc = SCNView.alloc().initWithFrame_options_(((0, 0),(100, 100)), ns({'SCNViewOptionPreferredRenderingAPI': 1})).autorelease()
        self._scene_objc.setAutoresizingMask_(18) # Fill superview
        self._scene_objc.setNeedsDisplayOnBoundsChange_(True) # fill on change
        self._scene_ref = None
        self._pointOfView_ref = Node(self._scene_objc.pointOfView())
    
    def attach(self):
        '''attach
            This function is called after __init__
            '''
        pass
    
    @property
    def showsStatistics(self):
        return self._scene_objc.showsStatistics()
    
    @showsStatistics.setter
    def showsStatistics(self, state):
        if type(state) == bool:
            self._scene_objc.setShowsStatistics_(state)
        else:
            raise TypeError('Must be a bool')

    @property
    def preferredFramesPerSecond(self):
        return self._scene_objc.preferredFramesPerSecond()
    
    @preferredFramesPerSecond.setter
    def preferredFramesPerSecond(self, value):
        self._scene_objc.setPreferredFramesPerSecond_(value)
    
    @property
    def allowsCameraControl(self):
        return self._scene_objc.allowsCameraControl()
    
    @allowsCameraControl.setter
    def allowsCameraControl(self, state):
        if type(state) == bool:
            self._scene_objc.setAllowsCameraControl_(state)
        else:
            raise TypeError('Must be a bool')

    @property
    def scene(self):
        if self._scene_ref:
            return self._scene_ref
        elif self._scene_objc.scene():
            raise Warning('The scene does not have a reference')
            return Scene(self._scene_objc.scene())
        else:
            return None

    @scene.setter
    def scene(self, value):
        if isinstance(value, (Scene)):
            self._scene_ref = value
            self._scene_objc.setScene_(value._objc)
        elif isinstance(value, (ObjCInstance)):
            self._scene_ref = Scene(value)
            self._scene_objc.setScene_(value)
        else:
            raise TypeError("Not able to set scene")

    @property
    def debugOptions(self):
        return DebugOptions(self._scene_objc.debugOptions())
    
    @debugOptions.setter
    def debugOptions(self, value):
        if isinstance(value, (DebugOptions)):
            self._scene_objc.setDebugOptions_(value.value)
        else:
            self._scene_objc.setDebugOptions_(int(value))

    @property
    def pointOfView(self):
        if self._scene_objc.pointOfView().ptr != self._pointOfView_ref._objc.ptr:
            self._pointOfView_ref = Node(self._scene_objc.pointOfView())
        return self._pointOfView_ref
    
    def setPointOfView(self, value, animate = True):
        if isinstance(value, (ObjCInstance)):
            self._pointOfView_ref = Node(value)
            self._scene_objc.setPointOfView_animate_(value, animate)
        if isinstance(value, (Node)):
            self._pointOfView_ref = value
            self._scene_objc.setPointOfView_animate_(value._objc, animate)

    def stop(self):
        self._scene_objc.stop_(None)
    
    def pause(self):
        self._scene_objc.pause_(None)
    
    def play(self):
        self._scene_objc.play_(None)

#--------SceneView---------
class SceneView (SKView):
	
    def attach(self):
        self.uiView = ui.View()
        self.present = self.uiView.present
        ObjCInstance(self.uiView).addSubview_(self._scene_objc)

#--------SceneTab(未使用)---------
class SceneTab (SceneView, TabView):
	
    def __init__(self):
        SceneView.__init__(self)
        TabView.__init__(self)
    
    @on_main_thread
    def makeSelf(self):
        self.name = "SceneKit"
    
    @on_main_thread
    def customVC(self):
        return create_objc_class(
                     "CustomViewController",
                     UIViewController,
                     methods = [],
                     protocols = ["OMTabContent"],
                   ).new()
    
    @on_main_thread
    def show(self):
        self.newVC.View = ObjCInstance(self.uiView)
        self.newVC.title = self.name
        self.newVC.navigationItem().rightBarButtonItems = self.right_button_items
        tabVC.addTabWithViewController_(self.newVC)

#--------Scene---------
class Scene (object):
	
    def __init__(self, scene = None):
        if scene:
            self._objc = objc
        else:
            self._objc = SCNScene.scene()
        self._node_ref = Node(self._objc.root())
    
    @property
    def playbackSpeed(self):
        return self._objc.playbackSpeed()
    
    @playbackSpeed.setter
    def playbackSpeed(self, value):
        self._objc.setPlaybackSpeed_(value)
    
    @property
    def framerate(self):
        return self._objc.frameRate()
    
    @framerate.setter
    def framerate(self, value):
        self._objc.setFrameRate_(value)
    
    @property
    def fogDensityExponent(self):
        '''
            Controls the attenuation between the start and end fog distances.
            0 means a constant fog, 1 a linear fog and 2 a quadratic fog,
            but any positive value will work.
            '''
        return self._objc.fogDensityExponent()
    
    @fogDensityExponent.setter
    def fogDensityExponent(self, value):
        self._objc.setFogDensityExponent_(value)
    
    @property
    def fogStartDistance(self):
        return self._objc.fogStartDistance()
    
    @fogStartDistance.setter
    def fogStartDistance(self, value):
        self._objc.setFogStartDistance_(value)
    
    @property
    def fogEndDistance(self):
        return self._objc.fogEndDistance()
    
    @fogEndDistance.setter
    def fogEndDistance(self, value):
        self._objc.setFogEndDistance_(value)
    
    @property
    def paused(self):
        return self._objc.isPaused()
    
    @paused.setter
    def paused(self, value):
        self._objc.setPaused_(value)
    
    @property
    def node(self):
        if self._node_ref._objc.ptr == self._objc.root().ptr: # checks so we domt use more memory
            return self._node_ref
        else:
            self._node_ref = Node(self._objc.root())
            return self._node_ref

    def removeAllParticleSystems(self):
        self._objc.removeAllParticleSystems()
    
    def save_to_file(self, file_name):
        if SUPPORTED_FORMATS.match(path.rsplit('.', 1)[-1]):
            options = ns({'SCNSceneExportDestinationURL': nsurl(path)})
            file = nsurl(file_name)
            
            return self._objc.writeToURL_options_(url, options)
        else:
            raise TypeError('Not a supported export type')

    def __repr__(self):
        return '<Scene <Framerate: {}, node: {}>>'.format(self.framerate, self.node)

# ------ Node ----------
class Node (object):
    def __init__(self, objc = None):
        self._light = None
        self._geometry = None
        self._camera = None
        self._child_ref = []
        if objc:
            self._objc = objc
            if self._objc.light():
                self._light = Light(objc=self._objc.light())
            if self._objc.geometry():
                self._geometry = Geometry(self._objc.geometry())
            if self._objc.camera():
                self._camera = Camera(self._objc.camera())
        else:
            self._objc = SCNNode.node()

    @property
    def childNodes(self):
        return self._child_ref
    
    @property
    def name(self):
        if self._objc.name():
            return str(self._objc.name())
        else:
            return None
    
    @name.setter
    def name(self, value):
        self._objc.setName_(value)
    
    @property
    def scale(self):
        return self._objc.scale()
    
    @scale.setter
    def scale(self, value):
        self._objc.setScale_(value)
    
    @property
    def transform(self):
        '''transfrom
            Note: with this you can not set properties directly
            '''
        return self._objc.transform(argtypes = [], restype = Matrix4)
    
    @transform.setter
    def transform(self, value):
        self._objc.setTransform_(value, argtypes = [Matrix4], restype = None)
    
    @property
    def position(self):
        return self._objc.position(argtypes = [], restype = Vector3)
    
    @position.setter
    def position(self, value):
        self._objc.setPosition_(value, argtypes = [Vector3], restype = None)
    
    @property
    def rotation(self):
        return self._objc.rotation()
    
    @rotation.setter
    def rotation(self, value):
        self._objc.setRotation_(value)
    
    @property
    def light(self):
        return self._light
    
    @light.setter
    def light(self, value):
        if isinstance(value, (ObjCInstance)):
            self._objc.setLight_(value)
            self._light = Light(value)
        if isinstance(value, (Light)):
            self._objc.setLight_(value._objc)
            self._light = value
        if value == None:
            self._objc.setLight_(value)
            self._light = value
    
    @property
    def geometry(self):
        return self._geometry
    
    @geometry.setter
    def geometry(self, value):
        if isinstance(value, (ObjCInstance)):
            self._objc.setGeometry_(value)
            self._geometry = Geometry(value)
        if isinstance(value, (Geometry)):
            self._objc.setGeometry_(value._objc)
            self._light = value
        if value == None:
            self._objc.setGeometry_(value)
            self._light = value
    
    @property
    def camera(self):
        return self._camera
    
    @camera.setter
    def camera(self, value):
        if isinstance(value, (ObjCInstance)):
            self._objc.setCamera_(value)
            self._camera = Camera(value)
        if isinstance(value, (Camera)):
            self._objc.setCamera_(value._objc)
            self._camera = value
        if value == None:
            self._objc.setCamera_(value)
            self._camera = value
    
    def clone(self):
        '''clone
            The copy is recursive: every child node will be cloned, too.
            The copied nodes will share their attached objects (light, geometry, camera, ...) with the original instances
            '''
        clone = self._objc.clone()
        return Node(clone)
    
    def flattenedClone(self):
        '''flattenedCLone
            A copy of the node with all geometry combined
            '''
        clone = self._objc.flattenedClone()
        return Node(clone)
    
    def addChild(self, value):
        if isinstance(value, (ObjCInstance)):
            if self._objc.canAddChildNode_(value):
                self._objc.addChildNode_(value)
                self._child_ref += [Node(value)]
        if isinstance(value, (Node)):
            if self._objc.canAddChildNode_(value._objc) and value not in self._child_ref:
                self._objc.addChildNode_(value._objc)
                self._child_ref += [value]

#--------- Light ------------
class Light (object):
	
    def __init__(self, kind = LightType.Omni, casts_shadow = True, shadow_sample_count = 1000, objc = None):
        if objc:
            self._objc = objc
        else:
            self._objc = SCNLight.light()
            self.type = kind
            self.castsShadow = casts_shadow
            self.shadowSampleCount = shadow_sample_count

    @property
    def type(self):
        return self._objc.type()
    
    @type.setter
    def type(self, kind):
        self._objc.setType_(kind)
    
    @property
    def castsShadow(self):
        return self._objc.castsShadow()
    
    @castsShadow.setter
    def castsShadow(self, value):
        self._objc.setCastsShadow_(value)
    
    @property
    def intensity(self):
        return self._objc.intensity()
    
    @intensity.setter
    def intensity(self, value):
        self._objc.setIntensity_(value)
    
    @property
    def shadowSampleCount(self):
        return self._objc.shadowSampleCount()
    
    @shadowSampleCount.setter
    def shadowSampleCount(self, value):
        self._objc.setShadowSampleCount_(value)
    
    @property
    def name(self):
        if self._objc.name():
            return str(self._objc.name())
        else:
            return None
    
    @name.setter
    def name(self, value):
        self._objc.setName_(value)
    
    @property
    def color(self):
        return self._objc.color()
    
    @color.setter
    def color(self, value):
        self._objc.setColor_(value)
    
    @property
    def shadowColor(self):
        return self._objc.color()
    
    @shadowColor.setter
    def shadowColor(self, value):
        self._objc.setShadowColor_(value)
    
    @property
    def shadowRadius(self):
        return self._objc.shadowRadius()
    
    @shadowRadius.setter
    def shadowRadius(self, value):
        self._objc.setShadowRadius(value)
    
    @property
    def shadowMapSize(self):
        return self._objc.shadowMapSize()
    
    @shadowMapSize.setter
    def shadowMapSize(self, value):
        self._objc.setShadowMapSize(value)

#--------- Camera ------------
class Camera (object):
	
    def __init__(self, objc = None):
        if objc:
            self._objc = objc
        else:
            self._objc = SCNCamera.camera()

    @property
    def name(self):
        if self._objc.name():
            return str(self._objc.name())
        else:
            return None
    
    @name.setter
    def name(self, value):
        self._objc.setName_(value)
    
    @property
    def xFov(self):
        '''Setting to 0 resets it to normal'''
        return self._objc.xFov()
    
    @xFov.setter
    def xFov(self, value):
        self._objc.setXFov_(value)
    
    @property
    def yFov(self):
        '''Setting to 0 resets it to normal'''
        return self._objc.yFov()
    
    @yFov.setter
    def yFov(self, value):
        self._objc.setYFov_(value)

# ---------- geometry ----------------
class Geometry (object):
	
    def __init__(self, objc = None):
        self._objc = objc
    
    @property
    def name(self):
        if self._objc.name():
            return str(self._objc.name())
        else:
            return None
    
    @name.setter
    def name(self, value):
        self._objc.setName_(value)
    
    @property
    def material(self):
        return Material(self._objc.material())


# --------- Material ------------
class Material (object):
	
    def __init__(self, objc = None):
        self._objc = objc
    
    @property
    def lightingModel(self):
        return str(self._objc.lightingModelName())
    
    @lightingModel.setter
    def lightingModel(self, value):
        if type(value) == str:
            self._objc.setLightingModelName_(value)
        else:
            print('not a valid type')

def load_scene(file):
    url = ns(file)
    s = SCNScene.sceneWithURL_options_(url, ns({}))
    return Scene(s)

#---------------
# Some 'constants' used by ARkit

class ARWorldAlignment(IntFlag):
    ARWorldAlignmentGravity = 0
    ARWorldAlignmentGravityAndHeading = 1
    ARWorldAlignmentCamera = 2

class ARPlaneDetection(IntFlag):
    ARPlaneDetectionNone = 0
    ARPlaneDetectionHorizontal = 1 << 0
    ARPlaneDetectionVertical = 1 << 1

# Work In Progress here, I(Brun0oO's)'m deciphering the ARKit constants...
class ARSCNDebugOption(IntFlag):
    ARSCNDebugOptionNone = 0
    ARSCNDebugOptionShowWorldOrigin = int("ffffffff80000000", 16)
    ARSCNDebugOptionShowFeaturePoints = int("ffffffff40000000", 16)

class ARSessionRunOptions(IntFlag):
    ARSessionRunOptionsNone                     = 0
    ARSessionRunOptionResetTracking             = 1 << 0
    ARSessionRunOptionRemoveExistingAnchors     = 1 << 1

def setDebugOptions(arscn, isShowInfo):
    if isShowInfo:
        arscn.setDebugOptions_(
            ARSCNDebugOptionShowFeaturePoints + ARSCNDebugOptionShowWorldOrigin
        )

def createARSceneView(x, y, w, h, debug=True):
    v = ARSCNView.alloc().initWithFrame_((CGRect(CGPoint(x, y), CGSize(w, h))))
    v.setShowsStatistics_(debug) # I love statistics...
    return v

def get_screen_size():
    bound =  UIScreen.mainScreen().bounds()
    return bound.size().width(), bound.size().height()

# -------------ヘルパー関数------------------
@on_main_thread
def get_screen_size():
    import dataclasses

    @dataclasses.dataclass
    class Screen:
        width: int
        height: int
    
    size = UIScreen.mainScreen().bounds().size
    return Screen(width=size.width, height=size.height)

@on_main_thread
def create_uiview(
        frame = (0, 0, 100, 100),
        flex='',
        backgroundColor = UIColor.color(red=1,green=1,blue=1,alpha=1.0),
        name = 'sample'
    ):
    rect = CGRect( CGPoint( frame[0], frame[1]),
                   CGSize(  frame[2], frame[3]) )
    ui_view = UIView.alloc().initWithFrame_(rect)
    ui_view.name = name
    ui_view.backgroundColor = backgroundColor
    return ui_view

@on_main_thread
def get_topcontroler():
    UIApplication = ObjCClass('UIApplication')
    # 自Windowのビューコントローラに対するポインタを手に入れる
    topController = UIApplication.sharedApplication().keyWindow().rootViewController()
    while topController.presentedViewController():
        topController = topController.presentedViewController()
    return topController

@on_main_thread
def get_view_controllers():
    #windows = UIApplication.sharedApplication().keyWindow()
    windows = UIApplication.sharedApplication().windows()
    return [w.rootViewController() for w in windows]

@on_main_thread
def get_mainview():
    return get_view_controllers()[1].view()

@on_main_thread
def add_uiview_to_mainview(uiview, main_view):
    main_view.addSubview_(uiview)
    #main_view.bringSubviewToFront_(uiview)

@on_main_thread
def add_uiview_to_superview(uiview, superview):
    super_view.addSubview_(uiview)

@on_main_thread
def remove_uiview_fromsuper(uiview):
    uiview.removeFromSuperview()
    uiview.hidden = True

# ************************************************************
class MyARView():
    
    def __init__(self):
        # 連動するSceneViewを保持する
        self.sceneview = None
        self.scene = None
        # arsessionも保持する
        self.arsession = None
        # 自デバイスの位置・向き・変換行列など
        self.position = None
        self.rotation = None
        self.transform = None
        self.eulerAngles = None
        # 画面タッチ時に処理をさせたい関数
        self.user_func_at_touch = None

    # ......delegate作成・画面作成など.......
    @on_main_thread
    def initialize(self, screen_xywh, isShowInfo):
        x, y, w, h = screen_xywh
        # Sceneを表示するSceneViewを作る
        self.sceneview = createARSceneView(x,y,w,h)

        def MyARSCNViewDelegate_renderer_didAdd_for_(_self, _cmd, scenerenderer, node, anchor):
            if not isinstance(anchor, (ARPlaneAnchor)):
                return

        def MyARSCNViewDelegate_session_didFailWithError_(_self,_cmd, _session, _error):
            print('error',_error,_cmd,_session)
            err_obj=ObjCInstance(_error)
            print(err_obj)

        def MyARSCNViewDelegate_renderer_willRenderScene_atTime_(_self, _cmd, scenerenderer, scene, time):
            pointOfView = self.sceneview.pointOfView()
            #transform = pointOfView.transform()
            self.rotation = pointOfView.rotation()
            self.position = pointOfView.position()
            self.transform = pointOfView.transform()
            self.eulerAngles = pointOfView.eulerAngles()
            return
        
        # delegate 処理をラップしたクラスを作る
        methods = [
            MyARSCNViewDelegate_renderer_didAdd_for_,
            MyARSCNViewDelegate_session_didFailWithError_,
            MyARSCNViewDelegate_renderer_willRenderScene_atTime_ ]
        protocols = [ 'ARSCNViewDelegate' ]
        MyARSCNViewDelegate = create_objc_class(
            'MyARSCNViewDelegate',
            NSObject,
            methods = methods,
            protocols = protocols)
        delegate = MyARSCNViewDelegate.alloc().init()
        # SceneViewをプロパティとして保持する
        self.sceneview.scene = self.scene
        # 作成したdelegateをSceneViewに設定する
        self.sceneview.setDelegate_(delegate)

        def CustomViewController_viewWillAppear_(_self, _cmd, animated):
            return

        def CustomViewController_viewWillDisappear_(_self, _cmd, animated):
            session = self.sceneview.session()
            session.pause()

        def CustomViewController_touchesBegan_withEvent_(_self, _cmd, _touches, event):
            touches = ObjCInstance(_touches)
            
            if self.user_func_at_touch:
                locations = []
                for t in touches:
                    loc = t.locationInView_(self.sceneview)
                locations.append(loc)
                self.user_func_at_touch(locations)
        # ViewController を作る
        methods = [
            CustomViewController_touchesBegan_withEvent_,
            CustomViewController_viewWillAppear_,
            CustomViewController_viewWillDisappear_]
        protocols = []
        # CustomViewControllerクラスを作る
        CustomViewController = create_objc_class(
            'CustomViewController',
            UIViewController,
            methods=methods,
            protocols=protocols )
        self.customViewController = CustomViewController.alloc().init()
        self.customViewController.view = self.sceneview
        # UIViewをmainViewに追加する
        main_view_vc = get_view_controllers()[1]
        main_view = main_view_vc.view()
        self.uiview = create_uiview()     # UIViewを作る
        add_uiview_to_mainview(self.uiview, main_view) # UIViewをmainViewに追加
        # CustomViewControllerを追加する
        main_view.addSubview_(self.sceneview) # UIViewにSceneViewを追加する
        main_view_vc.addChildViewController_(self.customViewController)
        self.customViewController.didMoveToParentViewController_(main_view_vc)

        # ARSessionを走らせる
        self.runARSession()
        # 必要に応じてデバッグ用設定をする
        setDebugOptions(self.sceneview, isShowInfo)

    @on_main_thread
    def runARSession(self):
        self.arsession = self.sceneview.session()
        # ARWorldTrackingConfigurationを作る
        arconfiguration = ARWorldTrackingConfiguration.alloc().init()
        # ARWorldTrackingConfiguration を設定していく
        arconfiguration.setPlaneDetection_(
            ARPlaneDetection.ARPlaneDetectionHorizontal )
        arconfiguration.setEnvironmentTexturing_( # 環境光マッピング
            AREnvironmentTexturingAutomatic )
        # どちらかを設定（今はARFrameSemanticSceneDepthを選んでいる）
        if ARWorldTrackingConfiguration.supportsFrameSemantics_(
                ARFrameSemanticSmoothedSceneDepth ):
            print("ARFrameSemanticSmoothedSceneDepth is enabled.")
            arconfiguration.frameSemantics = ARFrameSemanticSmoothedSceneDepth
            
        if ARWorldTrackingConfiguration.supportsFrameSemantics_(
                ARFrameSemanticSceneDepth ):
            print("ARFrameSemanticSceneDepth is enabled.")
            arconfiguration.frameSemantics = ARFrameSemanticSceneDepth
        # 使用可能なフォーマット
        for format in ARWorldTrackingConfiguration.supportedVideoFormats():
            pass
            #print( format )
        # ARSessionを走らせる
        self.arsession.runWithConfiguration_options_(
            arconfiguration,
            ARSessionRunOptions.ARSessionRunOptionResetTracking | ARSessionRunOptions.ARSessionRunOptionRemoveExistingAnchors )
        # ARSession が起動するのを待つ
        time.sleep(0.5)
    
    # ........SceneViewやUIViewを消す.......
    def close_view(self):
        remove_uiview_fromsuper(self.sceneview)
        remove_uiview_fromsuper(self.uiview)

    # .........ARSceneViewを止める..........
    def will_close(self):
        session = self.sceneview.session()
        session.pause()

    def process(self, process_user_f, pixelBuffer, depthData):
        # 色画像
        video_width = CVPixelBufferGetWidthOfPlane(pixelBuffer,0)
        video_height = CVPixelBufferGetHeightOfPlane(pixelBuffer,0)
        video_base_address = CVPixelBufferGetBaseAddressOfPlane(pixelBuffer,0)
        video_bytes_per_row = CVPixelBufferGetBytesPerRowOfPlane(pixelBuffer,0)

        # 距離マップ画像
        depth_width = CVPixelBufferGetWidthOfPlane(depthData,0)
        depth_height = CVPixelBufferGetHeightOfPlane(depthData,0)
        depth_base_address = CVPixelBufferGetBaseAddressOfPlane(depthData,0)
        depth_bytes_per_row = CVPixelBufferGetBytesPerRowOfPlane(depthData,0)
        if video_base_address is None or depth_base_address is None:
            return False
        video = np.ctypeslib.as_array(
                ctypes.cast(video_base_address, ctypes.POINTER(ctypes.c_ubyte)),
                shape=((video_height, video_width)) )
        depth = np.ctypeslib.as_array(
            ctypes.cast(depth_base_address, ctypes.POINTER(ctypes.c_float)),
            shape=( (depth_height, depth_width) ))
        # ユーザー指定の関数を呼ぶ
        process_user_f({
                #"video": ui2np(ci2ui(pixelBuffer2ci(pixelBuffer))),
                #"depth": copy.copy(depth)})
                "video": pixelBuffer,
                "depth": depth} )
        return True
    # .........色や距離画像を撮影する..........
    def capture_video_and_depth(self, process_user_f, is_smooth):
        frame = self.arsession.currentFrame()
        # 色画像へのピクセルバッファ
        pixelBuffer_color = frame.capturedImage()
        if is_smooth:
            smoothedSceneDepth = frame.smoothedSceneDepth()
        else:
            smoothedSceneDepth = frame.sceneDepth()
        if smoothedSceneDepth is None or pixelBuffer_color is None:
            print("smoothedSceneDepth or capturedImage is None.")
            return False
        else:
            # 距離マップ画像へのピクセルバッファ
            pixelBuffer_depth = smoothedSceneDepth.depthMap()
            # ピクセルバッファをロックする
            CVPixelBufferLockBaseAddress(pixelBuffer_color, 0)
            CVPixelBufferLockBaseAddress(pixelBuffer_depth, 0)
            # ユーザー作成の関数（process_user_f）を読んで、所望の処理をさせる
            result = self.process(process_user_f,
                pixelBuffer_color, pixelBuffer_depth)
            # ピクセルバッファのロックを解除する
            CVPixelBufferLockBaseAddress(pixelBuffer_color, 0)
            CVPixelBufferLockBaseAddress(pixelBuffer_depth, 0)
        return result

    @on_main_thread
    def add_element(
        self,
        _shape,        # 'sphere' or 'arrow'
        _color_array,  # (r,g,b,a)
        _size,         # size
        _length,       # length
        _pos,          # 位置
        _matrix):      # matrix

        # マテリアルを作成
        Material = SCNMaterial.material()
        Material.contents = UIColor.colorWithRed_green_blue_alpha_(
            _color_array[0],
            _color_array[1],
            _color_array[2],
            _color_array[3] )
        Material.lightingModel = LightingModel.PhysicallyBased
        # 指定された物体を追加する
        if 'sphere' == _shape and (not _pos is None):
            sphere_geometry = SCNSphere.sphereWithRadius_(_size)
            sphere_geometry.setMaterials_([Material])
            # 作成オブジェクトをnode＆rootに追加
            node = SCNNode.nodeWithGeometry_(sphere_geometry)
            self.scene.rootNode().addChildNode_(node)
            node.position = _pos
            return node
        if 'arrow' == _shape and (not _pos is None):
            # 槍中央部の円錐部
            cone_geometry = SCNCone.coneWithTopRadius_bottomRadius_height_(
                0,
                _size/5.0,
                _size/2.0 )
            cone_geometry.setMaterials_([Material])
            # 作成オブジェクトをSceneに追加
            cone_node = SCNNode.nodeWithGeometry_(cone_geometry)
            self.scene.rootNode().addChildNode_(cone_node)
            cone_node.position = _pos
            cone_node.rotation = _matrix
            # 槍の円筒部
            capsule_geometry = SCNCapsule.capsuleWithCapRadius_height_(
                _size/20.0,
                _length )
            capsule_geometry.setMaterials_([Material])
            # 作成オブジェクトをSceneに追加
            capsule_node = SCNNode.nodeWithGeometry_(capsule_geometry)
            self.scene.rootNode().addChildNode_(capsule_node)
            capsule_node.position = _pos
            capsule_node.rotation = _matrix
            return [cone_node, capsule_node]

    def initScene(self):
        self.scene = SCNScene.scene()

    def loadSceneAndAdd(self, file_path):
        # 3Dモデルを読み込む
        scene = SCNScene.sceneWithURL_options_(nsurl(file_path),None)
        # 3Dモデルのノードを手に入れ、Sceneに追加する
        node = scene.rootNode().childNodes().firstObject()
        self.scene.rootNode().addChildNode_(node)
        return node
    #========= Scene の初期設定を作る ===================
    def createSampleScene(self):
        self.scene = SCNScene.scene()
        self.root_node = self.scene.rootNode()
        self.cube_node = []
        self.gnum = 0
        # ......光源設定......（ここから)
        distanceOfLight = 1000
        # 点光源 1を作成
        light = SCNLight.light()
        light.setType_('omni')
        #light.setType_('directional')
        light.setColor_( UIColor.colorWithRed_green_blue_alpha_(0.8,1.0,0.9,1.0) )
        light_node = SCNNode.node()
        light_node.setLight_(light)
        light_node.setPosition((distanceOfLight, distanceOfLight, distanceOfLight))
        self.root_node.addChildNode_(light_node) # rootに追加
        # 点光源 2を作成
        light2 = SCNLight.light()
        light2.setType_('omni')
        light2.setColor_( UIColor.colorWithRed_green_blue_alpha_(1.0,0.7,0.9,1.0) )
        light_node2 = SCNNode.node()
        light_node2.setLight_(light2)
        light_node2.setPosition((-distanceOfLight, distanceOfLight, -distanceOfLight))
        self.root_node.addChildNode_(light_node2) # rootに追加
        # 点光源 3を作成
        light3 = SCNLight.light()
        light3.setType_('omni')
        light3.setColor_( UIColor.colorWithRed_green_blue_alpha_(0.7,0.7,1.0,1.0) )
        # 点光源 2を作成
        light_node3 = SCNNode.node()
        light_node3.setLight_(light3)
        light_node3.setPosition((distanceOfLight, distanceOfLight, -distanceOfLight))
        self.root_node.addChildNode_(light_node3) # rootに追加
        # ......光源設定......（ここまで)

# ************************************************************

# template for returning ('sphere' or 'arrow'), (r,g,b,a), size, length, matrix
def createNodeElementInfo():
    return 'sphere', [1.0, 1.0, 1.0, 0.5], 0.02, 0.02, 0

#==================================================================

if __name__ == '__main__':
    pass
