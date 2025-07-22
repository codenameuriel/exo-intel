from django.urls import path
from .views import TravelTimeSimulationView, SeasonalTempsSimulationView

app_name = "simulations"

urlpatterns = [
    path(
        "travel-time/",
        TravelTimeSimulationView.as_view(),
        name="simulation-travel-time",
    ),
    path(
        "seasonal-temps/",
        SeasonalTempsSimulationView.as_view(),
        name="simulation-seasonal-temps",
    ),
]
