from django.urls import path
from chat.views import MessageView

urlpatterns = [
    path("<int:course_id>", MessageView.as_view(), name="messages"),
]

app_name = "chat"
