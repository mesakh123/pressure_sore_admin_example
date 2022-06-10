from django.contrib import auth, messages
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponseForbidden,HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import base36_to_int, int_to_base36
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.base import TemplateResponseMixin, View,RedirectView
from django.views.generic.edit import FormView
from dashboard.models import PatientData,PredictResult,HandDocument,BurnDocument
from account.models import Account

# Create your views here.
class DashboardIndexView(TemplateResponseMixin, View):

    template_name = "dashboard/index.html"
    redirect_field_name = "account_login"

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(DashboardIndexView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect(self.get_redirect_url())
        ctx = self.get_context_data()
        return self.render_to_response(ctx)

    def post(self, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect(self.get_redirect_url())
        return redirect("dashboard")

    def get_context_data(self, **kwargs):
        ctx = kwargs
        redirect_field_name = self.get_redirect_field_name()
        ctx.update({
            "redirect_field_name": redirect_field_name,
            "redirect_field_value": self.request.POST.get(redirect_field_name, self.request.GET.get(redirect_field_name, "")),
        })
        return ctx

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        try:
            acc = Account.objects.filter(user=self.request.user)[0]
            return queryset.get(doctor=acc)
        except PatientData.DoesNotExist:
            raise Http404()

    def get_queryset(self):
        qs = PatientData.objects.all()
        qs = qs.select_related("doctor")
        return qs
    def get_redirect_field_name(self):
        return self.redirect_field_name
