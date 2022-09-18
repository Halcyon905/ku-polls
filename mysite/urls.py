from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from django.contrib.auth import urls

urlpatterns = [
    path("", lambda request: HttpResponseRedirect('polls/')),
    path("polls/", include("polls.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include(urls)),
]
