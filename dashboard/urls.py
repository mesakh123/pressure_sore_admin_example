from django.conf.urls import url
from dashboard.views import DashboardIndexView
urlpatterns = [
    url(r"^$",DashboardIndexView.as_view(), name="dashboard_index"),

]
