from django.contrib import admin
from django.urls import path,include

from . import views

app_name = "demo"

urlpatterns = [
    path("",views.burnupload , name="burnupload_url"),
    path("result",views.result , name="result_url"),
    path("inputdata",views.inputdata, name="inputdata_url"),
    #path("test",views.test, name="test_url"),
    path("feedbacksubmit/",views.feedbacksubmit, name="feedbacksubmit_url"),
]
