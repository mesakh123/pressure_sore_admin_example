from django.shortcuts import render,redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import translation
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.http import JsonResponse
from .forms import ContactForm
# Create your views here.

from django.views.generic import CreateView
from .models import Contact

class ContactCreateView(CreateView):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'subject', 'message')



def change_language(request):

    if request.method=="GET":
        return redirect(reverse("home"))
    lang = request.POST.get("language","")

    url = request.POST.get('url',"")
    data={
        'status':"fail"
    }
    if lang:
        if 'lang' in request.session:
            del request.session['lang']
        lang = lang[1:-1]
        translation.activate(lang)
        request.session['lang'] = lang
        data={
            'status':"success",
            'lang':lang
        }
    return JsonResponse(data)




def index(request):

    lang = None

    if request.method == "POST":

        form = ContactForm(request.POST)
        if form.is_valid():
            name =   form.cleaned_data['name']
            email =  form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            try:
                new_data = Contact(name=name, email=email,subject=subject,message=message)
                new_data.save()
                msgs = {'status':'OK'}
            except:
                msgs = {'status':'Fail'}
            return JsonResponse(msgs)

    if 'lang' in request.session:
        lang = request.session['lang']
        translation.activate(lang)
    form = ContactForm()
    return render(request,"main/index.html",locals())
