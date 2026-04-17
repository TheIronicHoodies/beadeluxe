from django.urls import path
from .views import SeatPlanView, UpdateSeatPlanView, RemoveSeatAssignmentView, AutoAssignSeatsView

urlpatterns = [
    path("<int:pk>/", SeatPlanView.as_view(), name="seat_plan"),
    path("update/", UpdateSeatPlanView.as_view(), name="update_seat_plan"),
    path("remove/", RemoveSeatAssignmentView.as_view(), name="remove_seat"),
    path("<int:pk>/auto-assign/", AutoAssignSeatsView.as_view(), name="auto_assign"),
]

app_name = "seat_plan"
