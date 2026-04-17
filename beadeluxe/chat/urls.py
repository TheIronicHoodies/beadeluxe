from django.urls import path
from chat.views import MessageView

urlpatterns = [
    path("<int:pk>/messages/", MessageView.as_view(), name="messages"),
    path("<int:pk>/messages/", MessageView.as_view(), name="messages"),
]

app_name = "chat"
