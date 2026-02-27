from django.urls import path
from .views import HomepageTemplateView

urlpatterns = [
    path('', HomepageTemplateView.as_view(), name='homepage'),
]
app_name = "home"