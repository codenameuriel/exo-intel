from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt
from .views import web, rest, graphql, simulations

app_name = "planets"

router = DefaultRouter()

router.register(r"planets", rest.PlanetViewSet, basename="planet")
router.register(r"starsystems", rest.StarSystemViewSet, basename="starsystem")
router.register(r"stars", rest.StarViewSet, basename="star")

urlpatterns = [
    path("", web.planets, name="planets"),
    path("api/", include(router.urls)),
    path("graphql/", csrf_exempt(graphql.PrivateGraphQLView.as_view()), name="graphql"),
    path(
        "api/simulations/travel-time/",
        simulations.TravelTimeSimulationView.as_view(),
        name="simulation-travel-time",
    ),
]
