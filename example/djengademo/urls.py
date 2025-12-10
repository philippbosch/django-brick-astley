"""
URL configuration for djengademo project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("djenga/", include("djenga.urls")),
]
