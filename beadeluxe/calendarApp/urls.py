from django.urls import path
from .views import (
CalendarView,
)

urlpatterns = [
    path('<int:course_id>/calendar/', 
         CalendarView.as_view(), 
         name='calendar'),
]

app_name = 'calendarApp'