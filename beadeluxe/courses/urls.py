from django.urls import path
from .views import course_list, course_detail
# from .views import CourseListView, CourseDetailView

urlpatterns = [
    path('', course_list, name="course_list"),
    path('<int:id>', course_detail, name="course_detail"),
    # path('list', CourseListView.as_view(), name='list'),
    # path('<int:id>/detail', CourseDetailView.as_view(), name='course-detail'),
]

app_name = "courses"
