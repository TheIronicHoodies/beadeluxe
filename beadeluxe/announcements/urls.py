from django.urls import path
from .views import (
    AnnouncementView,
    CreateAnnouncementView,
    EditAnnouncementView,
    DeleteAnnouncementView
)

urlpatterns = [
    path('<int:course_id>/announcements/', 
         AnnouncementView.as_view(), 
         name='announcement_list'),
    path('<int:course_id>/announcements/create/', 
         CreateAnnouncementView.as_view(), 
         name='announcement_create'),
    path('<int:course_id>/announcements/<int:announcement_id>/edit', 
         EditAnnouncementView.as_view(), 
         name='announcement_update'),
    path('<int:course_id>/announcements/<int:announcement_id>/delete/', 
         DeleteAnnouncementView.as_view(), 
         name='announcement_delete'),
]

app_name = 'announcements'