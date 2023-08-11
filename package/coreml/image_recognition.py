#!python3
'''
This is a demo of how you can use the CoreML framework (via objc_util) to classify images in Pythonista. It downloads the trained 'MobileNet' CoreML model from the Internet, and uses it to classify images that are either taken with the camera, or picked from the photo library.
'''

import requests
import os
import io
from PIL import Image
from objc_util.objc_util import ObjCClass, nsurl, ns

# Configuration (change URL and filename if you want to use a different model):
#MODEL_URL = 'https://docs-assets.developer.apple.com/coreml/models/MobileNet.mlmodel'
#MODEL_FILENAME = 'mobilenet.mlmodel'

# Use a local path for caching the model file (no need to sync this with iCloud):
#MODEL_PATH = os.getcwd()+'/models/'+MODEL_FILENAME

# Declare/import ObjC classes:
MLModel = ObjCClass('MLModel')
VNCoreMLModel = ObjCClass('VNCoreMLModel')
VNCoreMLRequest = ObjCClass('VNCoreMLRequest')
VNImageRequestHandler = ObjCClass('VNImageRequestHandler')

VNCoreMLFeatureValueObservation = ObjCClass('VNCoreMLFeatureValueObservation')
VNHumanBodyPoseObservation = ObjCClass('VNHumanBodyPoseObservation')

def load_model(
        MODEL_URL = 'https://docs-assets.developer.apple.com/coreml/models/MobileNet.mlmodel',
        MODEL_FILENAME = 'mobilenet.mlmodel',
        MODEL_PATH = os.getcwd()+'/models/'):
    MODEL_PATH = MODEL_PATH + MODEL_FILENAME
    # モデルがダウンロードされてなければ、ダウンロードする
    if not os.path.exists(MODEL_PATH):
        print(f'Downloading model: {MODEL_FILENAME}...')
        r = requests.get(MODEL_URL, stream=True)
        file_size = int(r.headers['content-length'])
        with open(MODEL_PATH, 'wb') as f:
            bytes_written = 0
            for chunk in r.iter_content(1024*100):
                f.write(chunk)
                print(f'{bytes_written/file_size*100:.2f}% downloaded')
                bytes_written += len(chunk)
        print('Download finished')
    ml_model_url = nsurl(MODEL_PATH)
    # モデルをコンパイルする
    c_model_url = MLModel.compileModelAtURL_error_(ml_model_url, None)
    # コンパイルされたモデルを読み込む
    ml_model = MLModel.modelWithContentsOfURL_error_(c_model_url, None)
    # MLModelから、VisionフレームワークのVNCoreMLModelを作る
    vn_model = VNCoreMLModel.modelForMLModel_error_(ml_model, None)
    return vn_model # 返り値はVNCoreMLModel

#-----------------------------------------------------------
def _classify_img_data(vn_model, img_data):
    # Create and perform the recognition request:
    req = VNCoreMLRequest.alloc().initWithModel_(vn_model).autorelease()
    handler = VNImageRequestHandler.alloc().initWithData_options_(img_data, None).autorelease()
    success = handler.performRequests_error_([req], None)
    if success:
        best_result = req.results()[0]
        label = str(best_result.identifier())
        confidence = best_result.confidence()
        return {'label': label, 'confidence': confidence}
    else:
        return None

def classify_image(vn_model, img):
    buffer = io.BytesIO()
    img.save(buffer, 'JPEG')
    img_data = ns(buffer.getvalue())
    return _classify_img_data(vn_model, img_data)

def classify_asset(vn_model, asset):
    img_data = ns(asset.get_image_data().getvalue())
    return _classify_img_data(img_data)
#-----------------------------------------------------------
def _performRequests_img_data(vn_model, img_data):
    # Create and perform the recognition request:
    req = VNCoreMLRequest.alloc().initWithModel_(vn_model).autorelease()
    handler = VNImageRequestHandler.alloc().initWithData_options_(img_data, None).autorelease()
    success = handler.performRequests_error_([req], None)
    if success:
        return req.results()
    else:
        return None

def performRequests_image(vn_model, img):
    buffer = io.BytesIO()
    img.save(buffer, 'JPEG')
    img_data = ns(buffer.getvalue())
    return _performRequests_img_data(vn_model, img_data)
#-----------------------------------------------------------
def scale_image(img, max_dim):
    '''Helper function to downscale an image for showing in the console'''
    scale = max_dim / max(img.size)
    w = int(img.size[0] * scale)
    h = int(img.size[1] * scale)
    return img.resize((w, h), Image.ANTIALIAS)

if __name__ == '__main__':
    print('')
    
