from django.urls import path
from . import views

urlpatterns = [
    path('', views.attendance_view, name='attendance'),
    path("update/", views.update_attendance, name="update_attendance"),
    path("session/add/<int:course_id>/", views.add_session, name="add_session"),
    path("session/delete/<int:session_id>/", views.delete_session, name="delete_session"),
]

app_name = 'attendance'