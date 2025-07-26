from django.urls import path
from .views import (
    TravelTimeSimulationView,
    SeasonalTempsSimulationView,
    TidalLockingSimulationView,
    StarLifetimeSimulationView,
    SimulationHistoryView,
)

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
    path(
        "tidal-locking/",
        TidalLockingSimulationView.as_view(),
        name="simulation-tidal-locking",
    ),
    path(
        "star-lifetime/",
        StarLifetimeSimulationView.as_view(),
        name="simulation-star-lifetime",
    ),
    path("history/", SimulationHistoryView.as_view(), name="simulation-history"),
]
