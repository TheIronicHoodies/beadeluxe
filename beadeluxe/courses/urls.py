from django.urls import path
from .views import CourseListView, CourseDetailView
from attendance.views import CourseAttendanceView
from seat_plan.views import SeatPlanView

urlpatterns = [
    path('', CourseListView.as_view(), name='list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='detail'),
    path("<int:pk>/attendance/", CourseAttendanceView.as_view(), name="course_attendance"),
    path("<int:pk>/seat_plan/", SeatPlanView.as_view(), name="course_seat_plan")
]

app_name = "courses"
