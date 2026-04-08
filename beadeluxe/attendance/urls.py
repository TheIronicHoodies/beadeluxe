from django.urls import path
from .views import (AttendanceView, CourseAttendanceView, UpdateAttendanceView, AddSessionView, DeleteSessionView)

urlpatterns = [
    path('', AttendanceView.as_view(), name='attendance'),
    path('update/', UpdateAttendanceView.as_view(), name='update_attendance'),
    path("session/add/<int:course_id>/", AddSessionView.as_view(), name="add_session"),
    path("session/delete/<int:session_id>/", DeleteSessionView.as_view(), name="delete_session"),
]

app_name = 'attendance'