"""This file sets up the urls for the user_management app."""
from django.urls import path
from .views import ProfileUpdateView 

urlpatterns = [
    path('', ProfileUpdateView.as_view(), name='profile-update'),
]
app_name = 'user_management'