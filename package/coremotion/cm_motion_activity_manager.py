# https://forum.omz-software.com/topic/3896/objc_tools-library/4

#from objc_util import ObjCClass, ObjCBlock, c_void_p, ObjCInstance,ns

import objc_util.objc_util as objc_util

NSDate = objc_util.ObjCClass('NSDate')

class MotionActivityManager:
    # コンストラクタ
    def __init__(self):
        self.CMMotionActivityManager = objc_util.ObjCClass('CMMotionActivityManager')
        self.CMMotionActivityManager_ = self.CMMotionActivityManager.alloc().init()
        self.create_activityData_handler()
        self.activity_data = []

    # アクティビティデータを初期化する
    def clear_activity_data(self):
        self.activity_data = []

    # アクティビティ取得時のハンドラー関数のオブジェクトを作る
    def create_activityData_handler(self):
        # アクティビティを得る関数ハンドラー用の関数
        def activityData_f(_cmd, _activityData, error):
            activityData = objc_util.ObjCInstance(_activityData)
            if not error == None:
                err = objc_util.ObjCInstance(error)
                print('error:'+str(err))
            else:
                s = str(activityData).replace('>',',').split(',')
                self.activity_data.append({
                    'confidence':s[4],
                    'stationary':s[8],
                    'walking':s[10],
                    'running':s[12],
                    'automotive':s[14],
                    'cycling':s[16],
                    'unknown':s[6] })
        # ハンドラーを登録する
        self.activityData_block = objc_util.ObjCBlock(
            activityData_f,
            restype=None,
            argtypes=[objc_util.c_void_p,
                      objc_util.c_void_p,
                      objc_util.c_void_p])
    
    def query_activity_from_date_to_date(self,fromDate,toDate):
        if self.CMMotionActivityManager.isActivityAvailable():
            NSOperationQueue = objc_util.ObjCClass('NSOperationQueue')
            # アクティビティを調べる
            self.CMMotionActivityManager_.queryActivityStartingFromDate_toDate_toQueue_withHandler_(
                objc_util.ns(fromDate),
                objc_util.ns(toDate),
                NSOperationQueue.mainQueue(),
                self.activityData_block)

