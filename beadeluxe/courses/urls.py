from django.urls import path
from .views import CourseListView, CourseDetailView, CourseCreateView

urlpatterns = [
    path('', CourseListView.as_view(), name='list'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('add/', CourseCreateView.as_view(), name='course-create'),
]

app_name = "courses"
