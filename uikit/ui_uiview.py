# coding: utf-8
# Copyright (c) 2018 Jun Hirabayashi (jun@hirax.net)
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php

from objc_util import *

UIView = ObjCClass('UIView')
UIApplication = ObjCClass('UIApplication')
UIScreen = ObjCClass('UIScreen')
UIImageView = ObjCClass('UIImageView')

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
def create_uiview(
        rect = CGRect(CGPoint(0,0),CGSize(100,100)),
        name = 'sample',
        color = UIColor.color(red=1,green=1,blue=1,alpha=0.5)
    ):
    ui_view = UIView.alloc().initWithFrame_(rect)
    ui_view.name = name
    ui_view.backgroundColor = color
    #ui_view.layer().masksToBounds = False #True
    return ui_view

@on_main_thread
def add_uiview_to_mainview(uiview, main_view):
    main_view.addSubview_(uiview)
    #main_view.bringSubviewToFront_(uiview)

@on_main_thread
def get_screen_bounds():
    return UIScreen.mainScreen().bounds()

@on_main_thread
def add_uiview_to_superview(uiview, superview):
    super_view.addSubview_(uiview)

@on_main_thread
def remove_uiview_fromsuper(uiview):
    uiview.removeFromSuperview()
    uiview.hidden = True

@on_main_thread
def create_uiview_full(name='sample'):
    size = get_screen_bounds().size
    ui_view = create_uiview(
        rect=CGRect( CGPoint(0, 0), CGSize(size.width, size.height)),
        name=name, color=UIColor.color(red=0,green=0,blue=0,alpha=1) )
