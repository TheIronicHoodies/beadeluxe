"""This file sets up the urls for the user_management app."""
from django.urls import path
from .views import ProfileUpdateView, ProfileForbiddenView, UserCreateView

urlpatterns = [
    path('forbidden', ProfileForbiddenView.as_view(), name='profile-forbidden'),
    path('create', UserCreateView.as_view(), name='profile-create'),
    path('<str:username>', ProfileUpdateView.as_view(), name='profile-update'),
]
app_name = 'user_management'