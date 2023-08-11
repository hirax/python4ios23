# coding: utf-8
# Copyright (c) 2018 Jun Hirabayashi (jun@hirax.net)
# Released under the MIT license
# https://opensource.org/licenses/mit-license.php

import rubicon_objc

# クラスオブジェクトへのポインタを得る
UIImpactFeedbackGenerator = rubicon_objc.api.ObjCClass('UIImpactFeedbackGenerator')
# インスタンス作成
UIImpactFeedbackGenerator_ = UIImpactFeedbackGenerator.alloc().init()
UIImpactFeedbackGenerator_.prepare()

# 触感フィードバックの種類を設定する
def initWithStyle( style = 0 ): # 0-4
    # Flat 記法
    UIImpactFeedbackGenerator_.initWithStyle_( style )
    # Interleave記法
    #UIImpactFeedbackGenerator_.initWithStyle( style )

# 触感フィードバックを発生させる
def impactOccurred():
    UIImpactFeedbackGenerator_.impactOccurred()
        
if __name__ == '__main__':
    # 触覚フィードバック生成
    initWithStyle( style = 0 )
    impactOccurred()
