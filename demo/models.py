from django.db import models
from datetime import datetime
# Create your models here.


class PatientData(models.Model):
    SEX_CHOICES = (
        ('f', 'Female',),
        ('m', 'Male',),
        ('u', 'Unsure',),
    )
    FREQ = (
        ("QD","QD"),
        ("BID","BID"),
        ("TID","TID"),
    )
    DRESSING_CHOICE= (
        ("wd","Wet Dressing"),
        ("oint","Ointment"),
        ("fd", "Fiber Dressing"),
        ("fod", "Foam Dressing"),
        ("vac", "VAC"),
        ("others", "Others"),
    )

    name = models.CharField(max_length=200)
    patient_id = models.CharField(max_length=200)
    age = models.IntegerField(default=0)
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,)
    fever = models.BooleanField(default=True)
    abnormal = models.BooleanField(default=True)
    hr = models.BooleanField(default=True)
    pus = models.BooleanField(default=True)
    odorous = models.BooleanField(default=True)
    undermine = models.BooleanField(default=True)
    frequency = models.CharField(default='QD',blank=True,choices=FREQ,max_length=10)
    dressing = models.CharField(default='wd',blank=True,choices=DRESSING_CHOICE,max_length=20)

    comments = models.TextField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        # Gives the proper plural name for admin
        verbose_name_plural = "PatientData"


    def __str__(self):
        return self.patient_id

    def get_dressing(self):
        return dict(self.DRESSING_CHOICE)[self.dressing]


class PredictResult(models.Model):
    medician_id = models.CharField(max_length=20, default="", blank=True, null=True)
    patient =  models.ForeignKey(PatientData, on_delete=models.SET_NULL,blank=True,null=True)
    predicted_time = models.DateTimeField(auto_now_add=True, blank=True)
    result_code = models.CharField(default='',blank=True,max_length=1024)
    predict_file = models.FileField(upload_to='documents/predict/file',blank=True,max_length=4096)
    distance = models.FloatField(default=0.0)
    predict_recommendation = models.CharField(default='',blank=True,max_length=1024)
    def __str__(self):
        return str(self.predicted_time)




class WoundDocument(models.Model):

    burn_choice = (
        ('Sacral','Sacral'),
        ('Trochanter','Trochanter'),
        ('Ischial','Ischial'),
        ('Occipital','Occipital'),
        ('Heel','Heel'),
        ('Ankle','Ankle'),
        ('Other','Other'),
    )
    burn_docfile_resized = models.ImageField(upload_to='documents/wound',blank=True)
    burn_docfile_ori = models.ImageField(upload_to='documents/wound',blank=True)
    file_location = models.CharField(default="",max_length=2048)
    burn_predict_docfile = models.ImageField(upload_to='documents/predict/wound',blank=True)
    predicted = models.BooleanField(default=False)
    process_predict = models.BooleanField(default=False)

    eschar_pixel = models.IntegerField(default=0)
    granulation_pixel = models.IntegerField(default=0)
    slough_pixel = models.IntegerField(default=0)
    ulceration_pixel = models.IntegerField(default=0)
    reep_pixel = models.IntegerField(default=0)

    distance = models.FloatField(default=10.0,blank=True)
    area = models.FloatField(default=10.0,blank=True)

    predict_result = models.ForeignKey(PredictResult, on_delete=models.SET_NULL,blank=True,null=True)
    wound_location =  models.CharField(max_length=250,choices=burn_choice,default='s',blank=True,null=True)
    surgerical_intervention = models.CharField(default="",max_length=2048)
    def __str__(self):
        return str(self.burn_docfile_resized.path)
