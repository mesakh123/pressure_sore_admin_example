from django.shortcuts import render,redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect,HttpResponse
from django.urls import reverse
import imghdr
from .models import WoundDocument,PatientData,PredictResult
from .forms import DocumentForm
import urllib.request as ulrequest
import base64
import io
from PIL import Image
from django.core.files import File
from django.core.files.uploadedfile import *
from django.core.files.temp import NamedTemporaryFile
import numpy as np
from .utils import resize_image
import cv2
import random
import string
import os
import shutil
import time
from pressure_sore_with_admin.settings import PLATFORMTYPE
from django.contrib import messages
from .grpc_request import predict_image_in_background


def calculate_lotion(patient_age,patient_weight,patient_height,tbsa):

    eight_hours = 0
    sixteen_hours = 0
    if patient_age < 15:
        result = (4*patient_weight) + 1500*pow(patient_weight*patient_height/3600,0.5)
        result /=24
        eight_hours = sixteen_hours=result
    else:
        if tbsa < 30:
            result = 2*patient_weight*tbsa
            eight_hours = result/16
            sixteen_hours = result / 32
        elif tbsa < 60:
            result = 2.5*patient_weight*tbsa
            eight_hours = result/16
            sixteen_hours = result / 32
        else:
            result = 3*patient_weight*tbsa
            eight_hours = result/16
            sixteen_hours = result / 32
    return eight_hours,sixteen_hours


def get_random_string(length):
    """
    Generate 'length' length of random characters
    """
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def inputdata(request):
    data = None
    demo_subdirectory=True
    if 'form-burn-submitted' not in request.session:
        return HttpResponseRedirect(reverse("demo:burnupload_url"))
    if request.method == "POST":
        if 'cleardata' in request.POST:
            try :
                del request.session['data']
                #del request.session['burn_image_session']
            except:
                pass
            return HttpResponseRedirect(reverse("demo:inputdata_url"))
        else :
            if 'data' in request.session:
                del request.session['data']
            data = {}
            msg = {}

            medicianid = request.POST.get('medicianid', '')
            data['medicianid'] = medicianid

            patientid = request.POST.get('patientid', '')
            data['patientid'] = patientid

            patientid = request.POST.get('patientid', '')
            data['patientid'] = patientid

            age = request.POST.get('age', '')
            data['age'] = age

            gender = request.POST.get('gender', '')
            data['gender'] = gender



            feveroption = request.POST.get('feveroption', '')
            data['feveroption'] = feveroption

            odorousoption = request.POST.get('odorousoption', '')
            data['odorousoption'] = odorousoption


            abnormaloption = request.POST.get('abnormaloption', '')
            data['abnormaloption'] = abnormaloption


            frequencyoption = request.POST.get('frequencyoption', '')
            data['frequencyoption'] = frequencyoption

            
            dressingoption = request.POST.get('dressingoption', '')
            data['dressingoption'] = dressingoption

            undermineoption = request.POST.get('undermineoption', '')
            data['undermineoption'] = undermineoption

            hroption = request.POST.get('hroption', '')
            data['hroption'] = hroption


            pusoption = request.POST.get('pusoption', '')
            data['pusoption'] = pusoption



            comments = request.POST.get('comments', '')
            data['comments'] = comments

            if data['patientid']=="" or data['medicianid'] == ""  or data['age']=="":
                messages.error(request,"ID ，年齡",extra_tags='alert alert-warning alert-dismissible fade show')
                return HttpResponseRedirect(reverse("demo:inputdata_url"))


            request.session['data'] =  data
            request.session['form-patient-submitted'] = True
            return HttpResponseRedirect(reverse("demo:result_url"))

    if 'data' in request.session:
        data = request.session['data']
    print(data)
    #del request.session['data']
    return render(request, "demo/inputdata.html", locals())

def upload_process(request,types="burn"):
    """
    Process images from base64 to numpy files, then resize to 512x512, then upload to database
    (because of our model XD)
    files : list of base64 Images.
    types : based on different types, upload to different database
    """
    base64_cookie = {}
    base64_cookie_hand=[]
    image_ids = []
    files = request.POST.getlist("images")
    woundlocation = request.POST.getlist("woundlocation")
    distances = request.POST.getlist("distance",'')

    for f,ft,d in zip(files,woundlocation,distances):
        if len(f.split(';base64,'))>1:
            format, f = f.split(';base64,')
            f = base64.b64decode(f)
            image_np = Image.open(io.BytesIO(f))
            image_np = np.asarray(image_np)
            image_np_resized, window, scale, padding, crop = resize_image(image_np,min_dim=1024, max_dim=1024)
            fileTemp = NamedTemporaryFile()
            fileTemp.write(f)
            filenameRe = get_random_string(15)
            f_ori = File(fileTemp, name=filenameRe+"-ori.png")

            #fileTemp = NamedTemporaryFile()
            #fileTemp.write()
            f_resized = File(fileTemp, name=filenameRe+"-resized.png")
            if types=="burn":
                newdoc = WoundDocument(burn_docfile_ori = f_ori,burn_docfile_resized=f_resized,distance=float(d))
            else:
                newdoc = HandDocument(hand_docfile_ori = f_ori,hand_docfile_resized=f_resized)

            newdoc.wound_location=str(ft)
            newdoc.save()

            file_location = str(newdoc).split("media")[1]
            if PLATFORMTYPE is "Windows":
                newdoc.file_location = "\media"+file_location.replace("ori",'resized')
            else:
                newdoc.file_location = "/media"+file_location.replace("ori",'resized')

            newdoc.save()
            image_np_resized = cv2.cvtColor(image_np_resized,cv2.COLOR_BGR2RGB)
            cv2.imwrite(str(newdoc),image_np_resized)
            image_ids.append(newdoc.id)
            file_name =str(newdoc)
            if types=="burn":
                if PLATFORMTYPE is 'Windows':
                    base64_cookie["\media"+file_name.split("media")[1].replace("ori",'resized')]=[ft,d]
                else:
                    base64_cookie["/media"+file_name.split("media")[1].replace("ori",'resized')]=[ft,d]
            else:
                if PLATFORMTYPE is 'Windows':
                    base64_cookie_hand.append("\media"+file_name.split("media")[1].replace("ori",'resized'))
                else:
                    base64_cookie_hand.append("/media"+file_name.split("media")[1].replace("ori",'resized'))


        else:
            if types=="burn":
                burn = WoundDocument.objects.get(file_location=f)
                id = burn.id
                base64_cookie[burn.file_location] = [ft,d]
                burn.wound_location = ft
                burn.distance = d
                burn.save()

            else:
                id = HandDocument.objects.get(file_location=f).id
            image_ids.append(id)

    if types=="burn":
        return base64_cookie,image_ids
    else:
        return base64_cookie_hand,image_ids

def predict_process(image_ids,types='burn'):
    for id in image_ids:
        if types=='burn':
            location = WoundDocument.objects.filter(pk=id).first()
        else:
            location = HandDocument.objects.filter(pk=id).first()
        if location.process_predict is False:
            location.process_predict = True
            location.save()
            predict_image_in_background(location.id,types)

def loading_database(image_ids,types='burn',predictResult=None):
    pixel_dict = {}
    image_dict = {}
    manual_tbsa = 0
    flag=True
    i = 0
    for id in image_ids:
        obj = None
        try:
            if types is 'burn':
                obj = WoundDocument.objects.get(pk=id)
            else:
                obj = HandDocument.objects.get(pk=id)
        except:
            pass
        if obj is not None:
            if obj.predicted:
                if types=='burn':
                    if int(obj.burn_pixel)!=0:
                        pixel_dict[i]=int(obj.burn_pixel)
                        image_dict[id] = str(obj.burn_predict_docfile)
                        manual_tbsa+=float(obj.user_calculated_tbsa)
                        i+=1
                    else:
                        image_dict[id] = str(obj.burn_docfile_resized)
                    obj.burn_result = predictResult
                else:
                    if int(obj.hand_pixel)!=0:
                        pixel_dict[i]=int(obj.hand_pixel)
                        image_dict[id] = str(obj.hand_predict_docfile)
                        i+=1
                    else:
                        image_dict[id] = str(obj.hand_docfile_resized)

                    obj.hand_result = predictResult
                obj.save()
            else:
                if obj.process_predict is False:
                    flag=False
    if types=="burn":
        return flag,pixel_dict,image_dict,manual_tbsa
    else:
        return flag,pixel_dict,image_dict

def loading_database_wound(image_ids,types='burn',predictResult=None):

    wound = list(WoundDocument.objects.filter(id__in=image_ids))
    classes  = [ 'Eschar','Granulation',"Slough",'Re-ep','Ulceration']
    image_data = ['pixels','area','distance']
    total_pixel_per_class = {}
    whole_total_pixels = 0
    whole_total_area = 0
    for c in classes:
        total_pixel_per_class[c]=0

    data_per_location = {}
    test = ""

    flag = True
    for i in range(len(wound)):
        if not wound[i].predicted :
            flag=False
            break
    if not flag:
        return flag,"","","",""



    for i in range(len(wound)):
        temp = wound[i]
        file_location = "/media/"+ str(wound[i].burn_predict_docfile)
        wound_location = temp.wound_location

        if wound_location not in data_per_location:
            
            dict_temp = {
                'images':[],
                'total_area':0,
                'total_pixels':{ 
                    c : 0 for c in classes
                },   
            }
            data_per_location[wound_location] = dict_temp.copy()

        pixels = [temp.eschar_pixel,temp.granulation_pixel,temp.slough_pixel,temp.reep_pixel,temp.ulceration_pixel]
        image_data = {
            'id':temp.id,
            'file_location':file_location,
            'pixels' : pixels,
            'distance' : temp.distance,
            'area' : (sum(pixels) * (42*31.5)**(temp.distance/35) )/ (1024*768),
        }
  

        if image_data not in data_per_location[wound_location]['images']:
            data_per_location[wound_location]['images'].append(image_data)
            
        for i in range(len(classes)):
            data_per_location[wound_location]['total_pixels'][classes[i]] += image_data['pixels'][i]

    #calculate total pixels from each location
    for wound_location in data_per_location:
        data = data_per_location[wound_location]
        
        for image in data['images']:
            for i in range(len(classes)):
                pixel_per_class = image['pixels'][i]
                total_pixel_per_class[classes[i]] += pixel_per_class
                whole_total_pixels += pixel_per_class
                

    #calculate area for each location
    for wound_location in data_per_location:
        total = 0

        for i in range(len(data_per_location[wound_location]['images'])):
            image = data_per_location[wound_location]['images'][i]
            temp_area = image['area']
            try:
                WoundDocument.objects.get(id=int(image['id'])).update(area = float(temp_area))
            except:
                pass
            total+= temp_area
            data_per_location[wound_location]['images'][i] = image
        data_per_location[wound_location]['total_area'] = total
        whole_total_area+=total
            

    return flag,data_per_location,whole_total_pixels,total_pixel_per_class,whole_total_area   


def inspectSurgericalIntervention(patientData,infectionStatus,data):

    #2
    necroticStatus = False
    granulationPercentage = data['pixels'][0] / data['total_pixels']
    if data['pixels'][2]!=0 or (granulationPercentage<0.6):
        necroticStatus=True

    #3
    underminingStatus = False
    if patientData.undermine or (patientData.frequency!="TID" and patientData.frequency!="More"):
        underminingStatus = True
    if infectionStatus or necroticStatus or underminingStatus:
        return True
    return False




"""

    for i in range(len(wound)):
        temp = wound[i]
        file_location = "/media/"+ str(wound[i].burn_predict_docfile)
        total_pixel_per_image[file_location] ={}
        
        for d in image_data:
            total_pixel_per_image[file_location][d]={}
        
        pixels = [temp.eschar_pixel,temp.granulation_pixel,temp.slough_pixel,temp.reep_pixel,temp.ulceration_pixel]
        for c,p in zip(classes,pixels):
            total_pixel_per_image[file_location]['pixels'][c]=float(p)
            total_pixel[c] += p

        
        total_pixel_per_image[file_location]['distance'] = temp.distance
        





        if temp.wound_location not in images_per_location:
            images_per_location[temp.wound_location]=[total_pixel_per_image]
        else:
            images_per_location[temp.wound_location].append(total_pixel_per_image)

        wound[i].burn_result=predictResult
        wound[i].save()

    reep_exists = True if total_pixel['Re-ep']>0 else False



    return flag,images_per_location,total_pixel,total_pixel_per_image,reep_exists
"""