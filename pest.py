import os
from flask import request
import io
import base64
import numpy as np
from PIL import Image
from keras.preprocessing.image import img_to_array

# Firebase 



class Pest(object):

    def __init__(self):
        self.APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        

    def Upload(self):
        target = os.path.join(self.APP_ROOT, 'static/images')
        print(target)

        if not os.path.isdir(target):
            os.mkdir(target)
        
        print(request.files.getlist("file"))

        for file in request.files.getlist("file"):
            print('come here')
            print(file)
            filename = file.filename
            print(filename)
            destination = "/".join([target, filename])
            print(destination)
            file.save(destination)
        
        
        default_image_size = tuple((256, 256))


        with open('static/images/'+filename, "rb") as fid:
            data = fid.read()

        b64_bytes = base64.b64encode(data)
        b64_string = b64_bytes.decode()

        try:
            image = Image.open(io.BytesIO(base64.b64decode(b64_string)))
            if image is not None :
                image = image.resize(default_image_size, Image.ANTIALIAS)   
                image_array = img_to_array(image)
                return np.expand_dims(image_array, axis=0),filename
            else:
                print("Error loading image file")
        except Exception as e:
            print(str(e))
