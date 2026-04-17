from django.urls import path
from chat.views import MessageView

urlpatterns = [
    path("<int:course_id>/messages/", MessageView.as_view(), name="messages"),
]

app_name = "chat"
