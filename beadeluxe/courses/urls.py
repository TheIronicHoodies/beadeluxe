from django.urls import path
from .views import CourseListView, CourseDetailView, CourseCreateView
from attendance.views import course_attendance_view

urlpatterns = [
    path('', CourseListView.as_view(), name='course_list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('add/', CourseCreateView.as_view(), name='course-create'),
    path("<int:course_id>/attendance/", course_attendance_view, name="course_attendance"),
]

app_name = "courses"
