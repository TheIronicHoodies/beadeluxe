"""This file sets up the urls for the user_management app."""
from django.urls import path
from .views import ProfileUpdateView 

urlpatterns = [
    path('<int:pk>', ProfileUpdateView.as_view(), name='profile-form'),
]

app_name = 'user_management'