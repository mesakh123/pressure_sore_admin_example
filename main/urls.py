from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url
from . import views
urlpatterns = [
    path("",views.index,name="home"),
    path("change_language",views.change_language,name="change_language"),

]
