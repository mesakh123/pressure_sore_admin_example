from django.contrib import admin
from main.models import Contact


# Register your models here.


class ContactAdmin(admin.ModelAdmin):

    list_display = ["name","email", "subject"]
    search_fields = ["name","email","subject" ]
    list_filter = ["name","email","created"]


admin.site.register(Contact,ContactAdmin)
