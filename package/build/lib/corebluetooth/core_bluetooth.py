import ctypes
from objc_util import *
from defines import *
import copy

# フレームワークを読み込む
CoreBluetooth = ctypes.cdll.LoadLibrary(
  "/System/Library/Frameworks/CoreBluetooth.framework/CoreBluetooth"
)
     
CBCentralManager = ObjCClass('CBCentralManager')
CBPeripheralManager = ObjCClass('CBPeripheralManager')
NSUUID = ObjCClass('NSUUID')
NSData = ObjCClass('NSData')
CBUUID = ObjCClass('CBUUID')
CBMutableCharacteristic = ObjCClass('CBMutableCharacteristic')
CBMutableService = ObjCClass('CBMutableService')

class CBCentralManagerEx:

    # コンストラクタ
    def __init__(self, process):
        # queueを作る
        self.queue = ObjCInstance(dispatch_get_current_queue())
        # delegate用関数を作る
        self.delegate = self.create_delegate()
        # CBCentralManagerを作る
        self.CBCentralManager = CBCentralManager.alloc().initWithDelegate_queue_(self.delegate, None)
        self.process = process

    def create_delegate(self):  #delegateを作る
        
        # central managerの状態が変化した時に呼ばれる関数を作る
        def centralManagerDidUpdateState_(_self, _cmd, _central): # CBCentralManager *
            _CBCentralManager = ObjCInstance(_central)
            state = _CBCentralManager.state()
            if state == CBCentralManagerStateUnknown:
                print("CBCentralManagerStateUnknown")
            if state == CBCentralManagerStateResetting:
                print("CBCentralManagerStateResetting")
            if state == CBCentralManagerStateUnsupported:
                print("CBCentralManagerStateUnsupported")
            if state == CBCentralManagerStatePoweredOff:
                print("CBCentralManagerStatePoweredOff")
            if state == CBCentralManagerStatePoweredOn:
                print("CBCentralManagerStatePoweredOn")
        
        # peripheralを発見した際に呼ばれる
        def centralManager_didDiscoverPeripheral_advertisementData_RSSI_(
                _self, _cmd, _central,
                _peripheral,
                _advertisementData, # アドバタイジング・パケットデータのNSDictionaryインスタンス
                _RSSI): # 受信信号強度: 10 * log I(mW) (dBm)
            
            # https://blog.reinforce-lab.com/post/2013-09-19-blebook-ch3-corebluetooth/
            
            _dict = {}
            
            rssi = ObjCInstance(_RSSI)
            _dict["RSSI"] = rssi.floatValue()
            
            # peripheral 情報
            if _peripheral is not None:
                peripheral = ObjCInstance(_peripheral)
                a_peripheral = {
                    "name": peripheral.name(),
                    "identifier":peripheral.identifier()}
                _dict["peripheral"] = a_peripheral
            # advertisementData
            if _advertisementData is not None:
                advertisementData = ObjCInstance(_advertisementData)
                
                print(advertisementData)
                
                # CBAdvertisementDataLocalNameKey
                if advertisementData["kCBAdvDataLocalName"] is not None:
                    _dict["LocalName"] = advertisementData["kCBAdvDataLocalName"]
                    # kCBAdvDataLocalName?

                # CBAdvDataLocalName
                #if advertisementData["kCBAdvDataLocalName"] is not None:
                #s    _dict["CBAdvDataLocalName"] = advertisementData["kCBAdvDataLocalName"]
                
                # kCBAdvDataManufacturerData があれば出力する
                if advertisementData["kCBAdvDataManufacturerData"] is not None:
                    advDataManufacturerData = advertisementData["kCBAdvDataManufacturerData"]
                    # Pythonバイト列に変換する
                    # Bluetooth SIGが企業に割り当てた2バイト識別子 + 任意データ
                    data = nsdata_to_bytes(advDataManufacturerData)
                    _dict["AdvDataManufacturerData"] = data
                    _dict["AdvDataManufacturerDataStr"] = data.hex()
                    
                    #uuid = NSUUID.alloc().initWithUUIDBytes_(
                    #    advDataManufacturerData.bytes() )
                # 送信電力(dbm)
                #if advertisementData["kCBAdvertisementDataTxPowerLevelKey"] is not None:
                if advertisementData["kCBAdvDataTxPowerLevel"] is not None:
                    _dict["AdvDataTxPowerLevel"] = advertisementData["kCBAdvDataTxPowerLevel"].floatValue()
                
                # 情報を使って何かする
                self.process(_dict)

        #delegate用クラスを作る
        # https://developer.apple.com/documentation/corebluetooth/cbcentralmanagerdelegate?language=objc
        CBCentralManagerDelegate = create_objc_class(
            'CBCentralManagerDelegate', # クラス名
                methods=[ centralManagerDidUpdateState_,
                          centralManager_didDiscoverPeripheral_advertisementData_RSSI_],
        protocols=['CBCentralManagerDelegate'])
        # delegateクラスをインスタンス化する
        return CBCentralManagerDelegate.new()
        
    def scanForPeripherals(self):
        # Bluetooth機器に対するスキャンを開始
        # 繰り返しのデータ取得をするには、CBCentralManagerScanOptionAllowDuplicatesKey をYESにする
        self.CBCentralManager.scanForPeripheralsWithServices_options_(
            None, # 使いたいサービス（配列） None→すべてのサービス
            None) # オプション

    def stopScan(self):
        self.CBCentralManager.stopScan()

        
class CBPeripheralManagerEx:

    # コンストラクタ
    def __init__(self):
        self.isService = False
        self.localName = ""
        # delegate用関数を作る
        self.delegate = self.create_delegate()
        # queueを作る
        self.queue = ObjCInstance(dispatch_get_current_queue())
        # CBCentralManagerを作る
        self.CBPeripheralManager = CBPeripheralManager.alloc().initWithDelegate_queue_(
            self.delegate, None)

    def add_service(self):  # 必須ではない
        self.characteristicUUID = CBUUID.UUIDWithString_("00000000-0000-0000-0000-000000000000")
        self.properties = CBCharacteristicPropertyRead # + CBCharacteristicPropertyWrite + CBCharacteristicPropertyNotify
        self.permissions = CBAttributePermissionsReadable #+ CBAttributePermissionsWriteable
        self.characteristic = CBMutableCharacteristic.alloc().initWithType_properties_value_permissions_(
            self.characteristicUUID,
            self.properties,
            None,
            self.permissions
        )
        # CBMutableServiceをつくる
        self.serviceUUID = CBUUID.UUIDWithString_("00000000-00000-0000-0000-000000000000")
        self.service = CBMutableService.alloc().initWithType_primary_(
            self.serviceUUID,
            True)
        self.service.characteristics = [self.characteristic]
        self.CBPeripheralManager.addService(self.service)
    
    def removeAllServices(self):
        self.CBPeripheralManager.removeAllServices()
        self.isService = False
            
    def set_localName(self, local_name):
        self.localName = local_name # ns("python")
        
    def create_delegate(self):  #delegateを作る
        
        # peripheral managerの状態が変化した時に呼ばれる関数を作る
        def peripheralManagerDidUpdateState_(_self, _cmd, _peripheral):
            _CBPeripheralManager = ObjCInstance(_peripheral)
            state = _CBPeripheralManager.state()
            if state == CBPeripheralManagerStateUnknown:
                print("CBCentralManagerStateUnknown")
            if state == CBPeripheralManagerStateResetting:
                print("CBPeripheralManagerStateResetting")
            if state == CBPeripheralManagerStateUnsupported:
                print("CBPeripheralManagerStateUnsupported")
            if state == CBPeripheralManagerStatePoweredOff:
                print("CBPeripheralManagerStatePoweredOff")
            if state == CBPeripheralManagerStatePoweredOn:
                print("CBPeripheralManagerStatePoweredOn")

        def peripheralManagerDidStartAdvertising_error_(_self, _cmd, _peripheral, _error):
            _CBPeripheralManager = ObjCInstance(_peripheral)
            if _error is None:
                print("Advertising starts without any error.")
            else:
                print(ObjCInstance(_error))
        
        def peripheralManager_didAddService_error_(_self, _cmd, _peripheral, _service,  _error):
            _CBPeripheralManager = ObjCInstance(_peripheral)
            if _error is None:
                self.isService = True
                print("Service is added without any error.")
            else:
                print(ObjCInstance(_error))
        
        #delegate用クラスを作る
        CBPeripheralManagerDelegate = create_objc_class(
            'CBPeripheralManagerDelegate', # クラス名
                methods=[
                    peripheralManagerDidUpdateState_,
                    peripheralManagerDidStartAdvertising_error_,
                    peripheralManager_didAddService_error_
                        ],
        protocols=['CBPeripheralManagerDelegate'])
        # delegateクラスをインスタンス化する
        
        return CBPeripheralManagerDelegate.new()
        
    def startAdvertising(self):
        if self.isService:
            self.advertisementData = {
                CBAdvertisementDataLocalNameKey: self.localName,
                CBAdvertisementDataServiceUUIDsKey: [ self.serviceUUID ]}
        else:
            self.advertisementData = {
                CBAdvertisementDataLocalNameKey: self.localName}
        self.CBPeripheralManager.startAdvertising_(self.advertisementData)
    
    def stopAdvertising(self):
        self.CBPeripheralManager.stopAdvertising()
