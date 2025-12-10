from django.shortcuts import render
from django.urls import path

urlpatterns = [
    path("", lambda r: render(r, "website/index.html"), name="home"),
]
