from django.urls import path
from .views import (
    CalendarView,
    CreateEventView,
    EditEventView,
    DeleteEventView,
    ToggleEventDoneView
)

urlpatterns = [
    path('<int:course_id>/calendar/', 
        CalendarView.as_view(), 
        name='calendar'),
    path('<int:course_id>/calendar/create/', 
        CreateEventView.as_view(), 
        name='event_create'),
    path('<int:course_id>/calendar/edit/<int:event_id>/', 
        EditEventView.as_view(), 
        name='event_edit'),
    path('<int:course_id>/calendar/delete/<int:event_id>/',
        DeleteEventView.as_view(),
        name='event_delete'),
    path("course/<int:course_id>/event/<int:event_id>/toggle/",
        ToggleEventDoneView.as_view(),
        name="toggle_event_done"),
]

app_name = 'calendarApp'