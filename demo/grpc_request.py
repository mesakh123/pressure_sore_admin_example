from background_task import background
import time
import cv2
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.base import ContentFile
from django.conf import settings
import numpy as np
from .mrcnn import visualize
from .models import WoundDocument,PatientData
import requests
import base64
import json
from PIL import Image
import io



BURN_MODEL = settings.BURN_MODEL
HAND_MODEL = settings.HAND_MODEL

from pressure_sore_with_admin.settings import PLATFORMTYPE
@background(schedule=0)
def predict_image_in_background(id,types='burn'):
    if types=='burn':
        class_names = ['BG', 'burn']
        location= WoundDocument.objects.filter(pk=id).first()
    else:
        class_names = ['BG','palm']
        location = HandDocument.objects.filter(pk=id).first()
    print("Predict hand started")

    if PLATFORMTYPE is 'Windows':
        folder , file_name = str(location).rsplit("\\",1)
    else:
        folder , file_name = str(location).rsplit("/",1)
    file_type = file_name.split(".")[-1]

    """
    image = cv2.imread(str(location),1)[:,:,::-1]
    retval, buffer = cv2.imencode("."+file_type, image)
    im_encode = base64.b64encode(buffer)
    """
    image = Image.open(str(location)).convert('RGB')
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    im_encode = base64.b64encode(buffer.getvalue()).decode("utf-8")
    print(f"BURN_MODEL ",BURN_MODEL)
    if types=='burn':
        print("Burn start")
        url = f"http://{BURN_MODEL}/v1/model_ps/zhang_pressure_sore:predict"
        #result = burn_detect_mask(image)
        result = requests.post(url, data=im_encode, timeout=600).json()
        predict_image_field = location.burn_predict_docfile
    else:
        url = f"http://{HAND_MODEL}/v1/models/mask_rcnn_hand_1000:predict"
        #result = hand_detect_mask(image)
        result = requests.post(url, data=im_encode, timeout=600).json()
        predict_image_field = location.hand_predict_docfile


    predict_result = result['result_image']
    decoded = base64.b64decode(predict_result)
    buffer = BytesIO(decoded)
    pillow_image = ContentFile(buffer.getvalue())

    predict_image_field.save(file_name,InMemoryUploadedFile(
            pillow_image,
            None,
            file_name,
            'image/jpeg',
            pillow_image.tell,
            None
        )
    )

    location.eschar_pixel = int(result['three_class_pixels']['0'])
    location.granulation_pixel = int(result['three_class_pixels']['1'])
    location.slough_pixel = int(result['three_class_pixels']['2'])


    location.reep_pixel = int(result['two_class_pixels']['0'])
    location.ulceration_pixel = int(result['two_class_pixels']['1'])

    location.predicted = True
    location.save()
    print("Predict success!")
"""    if types is 'burn':
        try:
            image = BurnDocument.objects.get(pk=id)
        except:
            image = 'empty'
        with open('output.txt','w') as f:
            f.write(str(image))
"""
