# https://forum.omz-software.com/topic/1935/how-can-i-convert-a-pil-image-to-a-ui-image/20

#import ui
import io
from PIL import ImageOps, ImageDraw
from PIL import Image
import numpy as np

from objc_util.objc_util import *

UIImage = ObjCClass('UIImage')

# numpy => pil (numpy, pillow機能で変換)
def np2pil(arrayIn):
    imgOut = Image.fromarray(arrayIn)
    return imgOut
    
# pil => numpy (numpy, pillow機能で変換)
def pil2np(imgIn,arrayOut=None):
    if arrayOut == None:
        arrayOut = np.array(imgIn)
        return arrayOut
    else:
        arrayOut[:] = np.array(imgIn)
        return None
        
# pil => ui (ui.Imageを使ってる)
def pil2ui(imgIn):  # PIL画像: imgIn
    with io.BytesIO() as bIO:
        imgIn.save(bIO, 'PNG')
        # imgOut = ui.Image.from_data( bIO.getvalue() )
        imgOut = UIImage.imageWithData_(bIO.getvalue())
        # あるいは
        #imgOut = UIImage.alloc()
        #imgOut.initWithData_(bIO.getvalue())
    del bIO
    return imgOut
    
# ui => pil
def ui2pil(imgIn):  #  UIImage: imgIn
    # create a fake png file in memory
    #memoryFile = StringIO.StringIO( imgIn.to_png() )
    
    # uiimage_to_png は objc_util に　UIImagePNGRepresentation
    # を使って実装されてる
    memoryFile = io.BytesIO( uiimage_to_png(imgIn) )

    # this creates the pil image, but does not read the data
    imgOut = Image.open(memoryFile)
    # this force the data to be read
    imgOut.load()
    # this releases the memory from the png file
    memoryFile.close()
    return imgOut
    
# numpy => pil => ui
def np2ui(arrayIn):
    # this is a lazy implementation, maybe could be more efficient?
    return pil2ui( np2pil(arrayIn) )
    
# ui => pil => numpy
def ui2np(imgIn):
    # this is a lazy implementation, maybe could be more efficient?
    return pil2np( ui2pil(imgIn) )

