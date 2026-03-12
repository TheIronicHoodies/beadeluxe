from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_view, name='attendance'),
    path("update/", views.update_attendance, name="update_attendance"),
]

app_name = 'attendance'