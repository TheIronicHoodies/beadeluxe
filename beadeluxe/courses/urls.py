from django.urls import path
from .views import CourseListView, CourseDetailView
from attendance.views import CourseAttendanceView

urlpatterns = [
    path('', CourseListView.as_view(), name='list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='detail'),
    path("<int:pk>/attendance/", CourseAttendanceView.as_view(), name="course_attendance"),
]

app_name = "courses"
