from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def home(request):
    return redirect("login")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),                
    path("", include("cloud_desk.urls")),
    path("accounts/", include("allauth.urls")),
]