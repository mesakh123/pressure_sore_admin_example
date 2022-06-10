import datetime
import functools
import operator
from urllib.parse import urlencode

from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.db import models, transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _

import pytz
from account import signals
from account.conf import settings
from account.fields import TimeZoneField
from account.hooks import hookset
from account.languages import DEFAULT_LANGUAGE
from account.managers import EmailAddressManager, EmailConfirmationManager
from account.signals import signup_code_sent, signup_code_used

from account.models import Account


# Create your models here.



class PatientData(models.Model):
    SEX_CHOICES = (
        ('f', 'Female',),
        ('m', 'Male',),
        ('u', 'Unsure',),
    )

    burn_choice = (
        ('s','Scald'),
        ('g','Grease'),
        ('n','Contact'),
        ('f','Flame'),
        ('c','Chemical'),
        ('e','Electric'),
        ('o','Other'),
    )
    doctor = models.ForeignKey(Account, on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=200)
    patient_id = models.CharField(max_length=200)
    age = models.IntegerField(default=0)
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,)
    height = models.FloatField()
    weight = models.FloatField()
    burn_type =  models.CharField(
        max_length=1,
        choices=burn_choice,)
    comments = models.TextField()
    created = models.DateTimeField(_("created"), default=timezone.now, editable=False, blank=True)
    def __str__(self):
        return self.patient_id

class PredictResult(models.Model):
    patient = models.ForeignKey(PatientData, on_delete=models.SET_NULL,null=True)
    predict_code = models.CharField(max_length=30)
    created = models.DateTimeField(_("created"), default=timezone.now, editable=False, blank=True)
    predict_tbsa_ai = models.FloatField(default=0)
    ai_after_eight_hours = models.FloatField(default=0)
    ai_after_sixteen_hours = models.FloatField(default=0)
    manual_tbsa = models.FloatField(default=0,blank=True)
    manual_after_eight_hours = models.FloatField(default=0)
    manual_after_sixteen_hours = models.FloatField(default=0)
    feedback_tbsa = models.FloatField(default=0)
    feedback_after_eight_hours = models.FloatField(default=0)
    feedback_after_sixteen_hours = models.FloatField(default=0)
    predict_file = models.FileField(upload_to='documents/predict/file',blank=True,max_length=4096)
    def __str__(self):
        return "%s %s" % (self.patient, self.created)


class HandDocument(models.Model):
    hand_docfile_resized = models.ImageField(upload_to='documents/hand',blank=True)
    hand_docfile_ori = models.ImageField(upload_to='documents/hand',blank=True)
    hand_predict_docfile = models.ImageField(upload_to='documents/predict/hand',blank=True)
    file_location = models.CharField(default="",max_length=2048)
    predicted = models.BooleanField(default=False)
    process_predict = models.BooleanField(default=False)
    hand_pixel = models.IntegerField(default=0)

    hand_result = models.OneToOneField(PredictResult, on_delete=models.SET_NULL,blank=True,null=True)
    def __str__(self):
        return str(self.hand_docfile_resized.path)

class BurnDocument(models.Model):
    burn_docfile_resized = models.ImageField(upload_to='documents/burn',blank=True)
    burn_docfile_ori = models.ImageField(upload_to='documents/burn',blank=True)
    file_location = models.CharField(default="",max_length=2048)
    burn_predict_docfile = models.ImageField(upload_to='documents/predict/burn',blank=True)
    predicted = models.BooleanField(default=False)
    process_predict = models.BooleanField(default=False)
    burn_pixel = models.IntegerField(default=0)
    burn_result = models.ForeignKey(PredictResult, on_delete=models.SET_NULL,blank=True,null=True)
    user_calculated_tbsa = models.FloatField(blank=True,null=True,default=0.0)
    def __str__(self):
        return str(self.burn_docfile_resized.path)
