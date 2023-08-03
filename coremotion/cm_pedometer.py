# https://forum.omz-software.com/topic/3896/objc_tools-library/4

#from objc_util import ObjCClass, ObjCBlock, c_void_p, ObjCInstance, ns

import objc_util

NSDate = objc_util.ObjCClass('NSDate')
        
class Pedometer:
    # コンストラクタ
    def __init__(self):
        # システム算出の歩数を得るためのCMPedometer
        self.CMPedometer = objc_util.ObjCClass('CMPedometer')
        self.CMPedometer_ = self.CMPedometer.alloc().init()
        self.create_pedometer_handler()
        self.pedometer_data = []

    # 歩数・距離情報を初期化する
    def clear_pedometer_data(self):
        self.pedometer_data = []

    # 歩数取得用ハンドラー
    def create_pedometer_handler(self):
        # 歩数を得る関数ハンドラー用の関数
        def get_pedometer_data_f(_cmd, _pedometerData, error):
            pedometer = objc_util.ObjCInstance(_pedometerData)
            if not error == None:
                err = objc_util.ObjCInstance(error)
                print('error:'+str(err))
            else:
                self.pedometer_data.append({
                    # NSNumberは所望の形式で値が出せる
                    # 単位は歩数
                    'numberOfSteps':pedometer.numberOfSteps().unsignedIntegerValue(),
                    'distance':pedometer.distance().floatValue() }) # 単位はm
        # ハンドラーを登録する
        self.pedometer_block = objc_util.ObjCBlock(
            get_pedometer_data_f,
            restype=None,
            argtypes=[
                objc_util.c_void_p,
                objc_util.c_void_p,
                objc_util.c_void_p])
    
    def query_pedometer_data_from_date_to_date(self,fromDate,toDate):
        if self.CMPedometer.isStepCountingAvailable():
            # 歩数を調べる
            self.CMPedometer_.queryPedometerDataFromDate_toDate_withHandler_(
                objc_util.ns(fromDate),
                objc_util.ns(toDate),
                self.pedometer_block)
        else:
            print('Unavailable')
            raise
