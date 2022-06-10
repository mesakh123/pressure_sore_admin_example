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
            flag,images_per_location,total_pixel,total_pixel_per_image,reep_exists = \
                loading_database_wound(wound_image_ids,'burn',predictResult)
            time.sleep(2)
            
            flag = True
            if flag :
                break
        #3.2
        total_overall=0
        if total_pixel != '':
            for k,v in total_pixel.items():
                total_overall+=v;
            if total_overall!=0:
                granulationPercentage = 100*total_pixel["Granulation"]/total_overall
            else:
                granulationPercentage = 0

            #3.1
            value1 = total_pixel["Granulation"]+total_pixel['Slough']+total_pixel['Eschar']
            value2 = total_pixel['Granulation']
            higherFlag = True
            dataChart1 = value2
            dataChart2 = value2/value1
            whole_total_area




            #3.4
            infectionStatus = getInfectionStatus(patientData)
            necroticStatus = False
            conditions2 = (total_pixel["Granulation"]/total_overall) if total_overall > 0 else 0
            if total_pixel['Eschar']!=0 or (conditions2<0.6 and total_overall>0):
                necroticStatus =True
            underminingStatus = False
            if patientData.undermine or (patientData.frequency!="TID" and patientData.frequency!="More"):
                underminingStatus = True

            surgericalInterventions = False
            if necroticStatus or infectionStatus or underminingStatus:
                surgericalInterventions = True
    clear = False

    if clear:
        try:
            for key in list(request.session.keys()):
                del request.session[key]
        except:
            pass
    if predictResult:
        request.session["feedback"] = predictResult.id

    return render(request, "demo/resultwound.html", locals())