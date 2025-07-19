from django.urls import path
from .views import TravelTimeSimulationView

app_name = "simulations"

urlpatterns = [
        path(
            "travel-time/",
            TravelTimeSimulationView.as_view(),
            name="simulation-travel-time",
    ),
]