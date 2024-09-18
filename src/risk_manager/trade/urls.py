"""Routes of the trade application are defined here"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('new/', views.new),
]
