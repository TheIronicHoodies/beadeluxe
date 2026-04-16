from django.urls import path
from .views import SeatPlanView, UpdateSeatPlanView, RemoveSeatAssignmentView

urlpatterns = [
    path("<int:pk>/", SeatPlanView.as_view(), name="seat_plan"),
    path("update/", UpdateSeatPlanView.as_view(), name="update_seat_plan"),
    path("remove/", RemoveSeatAssignmentView.as_view(), name="remove_seat"),
]

app_name = "seat_plan"
