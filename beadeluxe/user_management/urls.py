"""This file sets up the urls for the user_management app."""
from django.urls import path
from .views import ProfileForbiddenView, ProfileUpdateView, UserCreateView, ProfileDetailView

urlpatterns = [
    path('forbidden', ProfileForbiddenView.as_view(), name='profile-forbidden'),
    path('create', UserCreateView.as_view(), name='profile-create'),
    path('<str:username>', ProfileUpdateView.as_view(), name='profile-update'),
    path('view/<str:username>', ProfileDetailView.as_view(), name='profile-view'),
]
app_name = 'user_management'