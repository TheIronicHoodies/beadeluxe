from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_view, name='attendance'),
    path("course/<int:course_id>/", views.course_attendance_view, name="course_attendance"),
]

app_name = 'attendance'