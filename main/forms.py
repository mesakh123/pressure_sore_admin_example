from django import forms
from main.models import Contact
from django.utils.translation import gettext_lazy as _
# Create your forms here.

class ContactForm(forms.Form):
    name = forms.CharField(label = _('Name'), max_length = 50,min_length=3,required=True)
    email = forms.EmailField(label = _('Email'), max_length = 150,required=True)
    subject = forms.CharField(label = _('Subject'), max_length = 150,min_length=8,required=True)
    message = forms.CharField(label = _('Message'), widget = forms.Textarea, max_length = 2000,required=True)
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({
            'id': _('name'),
            'placeholder': _('Your Name'),
            'data-msg': _("Please enter at least 3 chars"),
            'data-rule':"minlen:3",
            'autocomplete':"off",
        })
        self.fields['email'].widget.attrs.update({
            'id': _('email'),
            'placeholder': _('Your Email'),
            'data-msg':_("Please enter a valid email"),
            'autocomplete':"off",
        })
        self.fields['subject'].widget.attrs.update({
            'id': _('subject'),
            'placeholder': _('Subject'),
            'data-msg':_("Please enter at least 8 chars of subject"),
            'data-rule':"minlen:8",
            'autocomplete':"off",
        })
        self.fields['message'].widget.attrs.update({
            'id': _('message'),
            'placeholder': _('Message'),
            'data-msg':_("Please write something for us"),
            'data-rule':"minlen:1",
            'autocomplete':"off",
        })
