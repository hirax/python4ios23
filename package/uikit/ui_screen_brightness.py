from objc_util.objc_util import *

@on_main_thread
def get_screen_brightness():
    UIScreen = ObjCClass('UIScreen')
    return float(UIScreen.mainScreen().brightness())

@on_main_thread
def set_screen_brightness(brightness):
    UIScreen = ObjCClass('UIScreen')
    UIScreen.mainScreen().brightness = brightness

if __name__ == '__main__':
    print(get_screen_brightness())
    set_screen_brightness(0.5)
