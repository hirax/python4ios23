from uikit.ui_uiimage_convert import *
from ctypes import *

CoreGraphics= cdll.LoadLibrary(
    "/System/Library/Frameworks/CoreGraphics.framework/CoreGraphics"
)

CIFilter = ObjCClass('CIFilter')
CIVector = ObjCClass('CIVector')
CIColor = ObjCClass('CIColor')
CIImage = ObjCClass('CIImage')

def pixelBuffer2ci(pixelBuffer):
    return CIImage.alloc().initWithCVPixelBuffer_(pixelBuffer)

def ui2cg(ui_img):
    return ObjCInstance(ui_img.CGImage())

def cg2ci(cg_img):
    return CIImage.alloc().initWithCGImage_(cg_img)

def ci2ui(ci_img):
    return UIImage.alloc().initWithCIImage_(ci_img)

def apply_filter2ci(ci_img, filter_name, dict):
    filter = CIFilter.filterWithName_(filter_name)
    filter.setValue_forKey_(ci_img, 'inputImage')
    for key in dict:
        filter.setValue_forKey_(dict[key], key)
    return filter.outputImage()

def apply_filter2np(np_image, filter_name, dict):
    ui_img = np2ui(np_image)
    cg_img = ui2cg(ui_img)
    ci_img = cg2ci(cg_img)
    ci_img = apply_filter2ci(ci_img, filter_name, dict)
    ui_img = ci2ui(ci_img)
    return ui2np(ui_img)
