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
from django.contrib import messages
from pressure_sore_with_admin.settings import PLATFORMTYPE
from .grpc_request import predict_image_in_background
from .views_utils import *
from django.http import JsonResponse
from io import StringIO
from django.core.files.base import ContentFile
import csv
from pressure_sore_with_admin import settings
from django.core.files import File
import datetime

def burnupload(request):
    wound_image_session = []
    image_ids = []
    image_urls = []
    demo_subdirectory=True

    if(request.method == "POST"):
        if len(request.POST.getlist("images")) is 0:
            message="File can't be empty"
            messages.error(request,message)
            return HttpResponseRedirect(reverse("demo:burnupload_url"))

        burn64_sess,image_ids =  upload_process(request,"burn")

        #session

        if "wound_image_session" not in request.session or len(burn64_sess)!=0:
            request.session["wound_image_session"] = burn64_sess
            request.session["wound_image_ids"] = image_ids
        request.session['form-burn-submitted'] = True
        if len(image_ids)!=0 or image_ids is not None:
            image_urls = predict_process(image_ids,'burn')
    else:
        if "wound_image_session" in request.session:
            wound_image_session = request.session.get("wound_image_session")
        if 'wound_image_ids' in request.session and "wound_image_session" in request.session:
            image_ids = request.session.get("wound_image_ids",None)

    return render(request, "demo/burnupload.html", locals())

def handupload(request):

    demo_subdirectory=True

    if 'form-burn-submitted' not in request.session:
        return HttpResponseRedirect(reverse("demo:burnupload_url"))
    hand_image_session = []
    image_ids = []
    if(request.method == "POST"):
        if len(request.POST.getlist("images")) is 0:
            message="File can't be empty"
        hand64_sess,image_ids =  upload_process(request.POST.getlist("images"),"hand",[0])
        if len(hand64_sess)!=0:
            request.session["hand_image_session"] = hand64_sess
            request.session["hand_image_ids"] = image_ids
        request.session['form-hand-submitted'] = True
        if image_ids is not None :
            image_urls = predict_process(image_ids,'palm')
    else:
        if "hand_image_session" in request.session  and request.session['hand_image_session'] is not None :
            hand_image_session = request.session.get("hand_image_session")
        if 'hand_image_ids' in request.session and "hand_image_session" in request.session:
            image_ids = request.session.get("hand_image_ids",None)

    return render(request, "demo/handupload.html", locals())

def result(request):
    demo_subdirectory=True
    result_code = ""
    predictResult = None
    manual_tbsa = None
    patient_id = ""
    patient_weight = 0
    patient_height = 0
    patient_age = 0
    weight = 0.0
    if 'form-patient-submitted' not in request.session and 'form-burn-submitted' not in request.session:

        return HttpResponseRedirect(reverse("demo:burnupload_url"))
    data = request.session.get("data",False)
    data_collection = {}
    if data:
        patient_id = data['patientid'] if data['patientid'] is not '' else ''
        medician_id = data['medicianid'] if data['medicianid'] is not '' else ''
        if patient_id:
            result_code = patient_id+datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
        else:
            message="Required datas can't be empty"
            messages.error(request,message)
            return HttpResponseRedirect(reverse("demo:inputdata"))
        #patient_weight = float(data['weight']) if data['weight'] is not '' else 2.0
        #patient_height = float(data['height']) if data['height'] is not '' else 100.0
        patient_age = int(data['age']) if data['age'] is not '' else 1
        patient_fever = True if data['feveroption']=="True" else False
        patient_odor = True if data['odorousoption']=="True" else False
        patient_abnormal =  True if data['abnormaloption']=="True" else False
        patient_frequency = str(data['frequencyoption']).upper() if data['frequencyoption']!="" else "QD"
        patient_undermine = True if data['undermineoption']=="True" else False
        patient_hr = True if data['hroption']=="True" else False
        patient_pus = True if data['pusoption']=="True" else False
        patient_dressing = str(data['dressingoption']) if data['dressingoption']!="" else "wd"

        patientData = PatientData(
            patient_id = patient_id,
            age = patient_age,
            sex = data['gender'] if data['gender'] is not '' else '',
            fever = patient_fever,
            odorous = patient_odor,
            abnormal = patient_abnormal,
            frequency = patient_frequency ,
            undermine = patient_undermine,
            hr = patient_hr,
            pus = patient_pus,
            comments = data['comments'],
            dressing = patient_dressing
        )
        patientData.save()
        predictResult = PredictResult()
        if "wound_image_ids" in request.session:
            wound_image_ids = request.session.get("wound_image_ids")
        if "hand_image_ids" in request.session:
            hand_image_ids = request.session.get("hand_image_ids")
        predictResult.patient=patientData
        predictResult.medician_id = medician_id
        predictResult.result_code = result_code
        predictResult.save()


        for wound_id in wound_image_ids:
            try:
                wound = WoundDocument.objects.get(id=wound_id)
                wound.predict_result = predictResult
                wound.save()
            except:
                continue
                
       
        #init
        while True:
            
            flag = True
            
            #3.3 - 1 whole_total_area
            flag,data_per_location,whole_total_pixels,total_pixel_per_class,whole_total_area  = \
                    loading_database_wound(wound_image_ids,'burn',predictResult)
            time.sleep(1)
            
            if flag :
                break
        
        
        #3.1
        reep_exists = True if int(total_pixel_per_class['Re-ep']) else False
        

        #3.2 granulation/total
        value1 = total_pixel_per_class["Granulation"]+total_pixel_per_class['Slough']+total_pixel_per_class['Eschar']
        value2 = total_pixel_per_class['Granulation']
        value3 = total_pixel_per_class['Slough']+total_pixel_per_class['Eschar']
        value4 = total_pixel_per_class['Eschar']
        value5 = total_pixel_per_class['Slough']
        
        dataChart1 = value2
        granulationPercentage = 100*value2/value1 if value1 else 0.0
        

        #3.4-1
        underminingStatus = False
        if patientData.undermine or (patientData.frequency=="TID"):
            underminingStatus = True
               
        infectionStatus = getInfectionStatus(patientData)


        #3.3-2 area per wound location

        temp={}
        for wound_location,data_dict in data_per_location.items():
            if wound_location not in data_collection:
                data_collection[wound_location] = {}
            
            if 'imageData' not in data_collection[wound_location]:
                data_collection[wound_location]['imageData'] = []

            

            temp = {}
            for image_id,enum_data in zip(wound_image_ids,enumerate(data_dict['images'])):
                i,data = enum_data
                try:
                    wound = WoundDocument.objects.get(id=image_id)
                except:
                    wound = None


                temp[i] = {}
                temp[i]['file_location']=data['file_location']
                temp[i]['pixels'] = [data['pixels'][1],\
                    data['pixels'][0]+data['pixels'][2],data['pixels'][0],data['pixels'][2]]
                temp[i]['reep_exists']= True if data['pixels'][3] else False
                #3.4-2
                necroticStatus = False
                conditions2 = data['pixels'][1] / (data['pixels'][0]+data['pixels'][1]+data['pixels'][2]) if  (data['pixels'][0]+data['pixels'][1]+data['pixels'][2]) else 0.0
                temp[i]['percentage'] = conditions2*100
                if data['pixels'][0]!=0 or (conditions2<0.4):
                    necroticStatus =True
                temp[i]['surgericalIntervention'] = False
                temp[i]['area'] = data['area']
                if underminingStatus or necroticStatus or infectionStatus:
                    temp[i]['surgericalIntervention'] = True
                if wound:
                    if temp[i]['surgericalIntervention'] :
                        wound.surgerical_intervention = r"可能需要清創手術"
                    else:
                        wound.surgerical_intervention = r"持續傷口照護"
                    wound.save()
            data_collection[wound_location]['imageData'] = temp

    clear = True
    list_key = ['wound_image_session','wound_image_ids','form-burn-submitted','form-patient-submitted','feedback','data']
    
    if clear:
        try:
            for key in list_key:
                del request.session[key]
        except:
            pass
    if predictResult:
        request.session["feedback"] = predictResult.id


    return render(request, "demo/resultwound.html", locals())




def feedbacksubmit(request):
    if request.method=="POST" and request.is_ajax:

        result_code = request.POST.get("result_code",None)
        feedback_tbsa = request.POST.get("feedback_tbsa",None)
        feedback_8 = request.POST.get("feedback_8",None)
        feedback_16 = request.POST.get("feedback_16",None)
        manual_tbsa = None
        patient_id = ""

        if "manual_tbsa" in request.session:
            manual_tbsa = request.session["manual_tbsa"]

        if result_code and feedback_tbsa and feedback_8 and feedback_16 :
            try:
                predictResult = PredictResult.objects.get(result_code=result_code)
            except PredictResult.DoesNotExist:
                predictResult =None
            if predictResult:
                patient = predictResult.patient

                list_left = ["病人ID","識別碼","姓名","性別","年齡","身高","體重","燙傷類別","AI判斷TBSA","AI判斷前8小時點","AI判斷後16小時點",
                "使用者手動輸入TBSA", "使用者手動輸入TBSA前8小時點","使用者手動輸入TBSA後16小時點","使用者回饋TBSA","使用者回饋TBSA前8小時點","使用者回饋TBSA前16小時點",]
                list_right = [patient.patient_id, result_code,patient.name,patient.sex,patient.age,patient.height,patient.weight,patient.wound_location,
                    predictResult.predict_tbsa_ai,predictResult.ai_after_eight_hours,predictResult.ai_after_sixteen_hours,
                    manual_tbsa,predictResult.manual_after_eight_hours,predictResult.manual_after_sixteen_hours,feedback_tbsa,feedback_8,feedback_16]
                predictResult.feedback_tbsa =feedback_tbsa
                predictResult.feedback_after_eight_hours = feedback_8
                predictResult.feedback_after_sixteen_hours = feedback_16
                patient_id = patient.patient_id
                rows = zip(list_left,list_right)

                path = os.path.join(settings.MEDIA_ROOT, 'documents', 'predict', 'file',patient_id+'_'+result_code+'.csv')
                if os.path.exists(path):
                    os.remove(path)
                if patient_id is "":
                    path = result_code+".csv"
                else:
                    path = patient_id+".csv"
                csv_buffer = StringIO()
                csv_writer = csv.writer(csv_buffer)
                for row in rows:
                    csv_writer.writerow(row)
                csv_file = ContentFile(csv_buffer.getvalue().encode('utf-8'))

                predictResult.predict_file.save(path,csv_file)
                predictResult.save()
                response = {
                     'msg':'Your form has been submitted successfully', # response message
                     'file_url': "/media/"+str(predictResult.predict_file),
                     'file_name': path,
                }
                return JsonResponse(response) # return response as JSON
    response = {
         'msg':'Your form has been failed to submit' # response message
    }
    return JsonResponse(response) # return response as JSON



def getInfectionStatus(patient):
    total = 0
    total += 1.5 if patient.pus else 0
    total += 1 if patient.odorous else 0
    total += 0.5 if patient.fever else 0
    total += 0.5 if patient.abnormal else 0
    total += 0.5 if patient.hr else 0

    if total>=1.5:
        return True
    return False



def test(request):
    id_list = [78,79]



    temp = list(request.session.items())
    demo_subdirectory=True
    result_code = ""
    predictResult = None
    manual_tbsa = None
    patient_id = ""
    patient_weight = 0
    patient_height = 0
    patient_age = 0
    weight = 0.0
    if 'form-patient-submitted' not in request.session and 'form-burn-submitted' not in request.session:

        return HttpResponseRedirect(reverse("demo:burnupload_url"))
    data = request.session.get("data",False)
    data_collection = {}
    if data:
        patient_id = data['patientid'] if data['patientid'] is not '' else ''
        if patient_id:
            result_code = patient_id+datetime.datetime.now().strftime('%Y%m%d%H:%M:%S')
        else:
            message="Required datas can't be empty"
            messages.error(request,message)
            return HttpResponseRedirect(reverse("demo:inputdata"))
        #patient_weight = float(data['weight']) if data['weight'] is not '' else 2.0
        #patient_height = float(data['height']) if data['height'] is not '' else 100.0
        patient_age = int(data['age']) if data['age'] is not '' else 1
        patient_fever = True if data['feveroption']=="True" else False
        patient_odor = True if data['odorousoption']=="True" else False
        patient_abnormal =  True if data['abnormaloption']=="True" else False
        patient_frequency = str(data['frequencyoption']).upper() if data['frequencyoption']!="" else "QD"
        patient_undermine = True if data['undermineoption']=="True" else False
        patient_hr = True if data['hroption']=="True" else False
        patient_pus = True if data['pusoption']=="True" else False

        patientData = PatientData(
            name = data['name'] if data['name'] is not '' else '',
            patient_id = patient_id,
            age = patient_age,
            sex = data['gender'] if data['gender'] is not '' else '',
            fever = patient_fever,
            odorous = patient_odor,
            abnormal = patient_abnormal,
            frequency = patient_frequency ,
            undermine = patient_undermine,
            hr = patient_hr,
            pus = patient_pus,
            comments = data['comments']
        )
        patientData.save()
        predictResult = PredictResult()
        if "wound_image_ids" in request.session:
            wound_image_ids = request.session.get("wound_image_ids")
        if "hand_image_ids" in request.session:
            hand_image_ids = request.session.get("hand_image_ids")
        predictResult.patient=patientData
        predictResult.result_code = result_code
        predictResult.save()
        #init
        while True:
            
            flag = True
            
            #3.3 - 1 whole_total_area
            flag,data_per_location,whole_total_pixels,total_pixel_per_class,whole_total_area  = \
                    loading_database_wound(wound_image_ids,'burn',predictResult)
            time.sleep(1)
            
            if flag :
                break
        
        
        #3.1
        reep_exists = True if int(total_pixel_per_class['Re-ep']) else False
        

        #3.2 granulation/total
        value1 = total_pixel_per_class["Granulation"]+total_pixel_per_class['Slough']+total_pixel_per_class['Eschar']
        value2 = total_pixel_per_class['Granulation']
        value3 = total_pixel_per_class['Slough']+total_pixel_per_class['Eschar']
        value4 = total_pixel_per_class['Eschar']
        value5 = total_pixel_per_class['Slough']
        
        dataChart1 = value2
        granulationPercentage = 100*value2/value1
        

        #3.4-1
        underminingStatus = False
        print("patientdata undermine",patientData.undermine)
        if patientData.undermine or (patientData.frequency=="TID"):
            underminingStatus = True
               
        infectionStatus = getInfectionStatus(patientData)


        #3.3-2 area per wound location

        temp={}
        for wound_location,data_dict in data_per_location.items():
            if wound_location not in data_collection:
                data_collection[wound_location] = {}
            
            if 'imageData' not in data_collection[wound_location]:
                data_collection[wound_location]['imageData'] = []

            

            temp = {}
            for i,data in enumerate(data_dict['images']):
                temp[i] = {}
                temp[i]['file_location']=data['file_location']
                temp[i]['pixels'] = [data['pixels'][1],\
                    data['pixels'][0]+data['pixels'][2],data['pixels'][0],data['pixels'][2]]
                temp[i]['reep_exists']= True if data['pixels'][0] else False
                #3.4-2
                necroticStatus = False
                conditions2 = data['pixels'][1] / (data['pixels'][0]+data['pixels'][1]+data['pixels'][2])
                temp[i]['percentage'] = conditions2*100
                if data['pixels'][0]!=0 or (conditions2<0.4):
                    necroticStatus =True
                temp[i]['surgericalIntervention'] = False
                temp[i]['area'] = data['area']
                if underminingStatus or necroticStatus or infectionStatus:
                    temp[i]['surgericalIntervention'] = True
               
            data_collection[wound_location]['imageData'] = temp

    clear = False

    if clear:
        try:
            for key in list(request.session.keys()):
                del request.session[key]
        except:
            pass
    if predictResult:
        request.session["feedback"] = predictResult.id



    return render(request, "demo/test.html", locals())

