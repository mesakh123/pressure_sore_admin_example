from django.contrib import admin
from dashboard.models import PatientData,PredictResult,HandDocument,BurnDocument


# Register your models here.


class ContactAdmin(admin.ModelAdmin):

    list_display = ["name","email", "subject"]
    search_fields = ["name","email","subject" ]
    list_filter = ["name","email","created"]
