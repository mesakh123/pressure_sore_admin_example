from django.contrib import admin
from .models import PatientData,WoundDocument,PredictResult
# Register your models here.


class PatientDataAdmin(admin.ModelAdmin):
    list_display = ["patient_id",'updated','name']
    readonly_fields = ('created','updated')
    search_fields = ('patient_id','name',)
class PredictResultAdmin(admin.ModelAdmin):
    search_fields = ('result_code', )
    readonly_fields = ('predicted_time',)
class WoundDocumentAdmin(admin.ModelAdmin):
    search_fields = ('predict_result__patient__patient_id', )
admin.site.register(PatientData,PatientDataAdmin)
admin.site.register(WoundDocument,WoundDocumentAdmin)
admin.site.register(PredictResult,PredictResultAdmin)
