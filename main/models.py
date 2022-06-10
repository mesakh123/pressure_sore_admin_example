from django.db import models

from django.utils import timezone, translation
from django.utils.translation import gettext_lazy as _
# Create your models here.
class Contact(models.Model):
    name = models.CharField(blank=False,max_length=128)
    email = models.EmailField(blank=False,max_length=128)
    subject = models.CharField(blank=False,max_length=128)
    message = models.TextField(blank=False)
    created = models.DateTimeField(_("created"), default=timezone.now, editable=False, blank=True)
    def __str__(self):
        return self.name
