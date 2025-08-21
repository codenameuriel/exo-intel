from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter

from .views import graphql, rest, web

app_name = "api"

router = DefaultRouter()

router.register(r"planets", rest.PlanetViewSet, basename="planet")
router.register(r"starsystems", rest.StarSystemViewSet, basename="starsystem")
router.register(r"stars", rest.StarViewSet, basename="star")

urlpatterns = [
    path("", web.planets, name="planets"),
    path("rest/", include(router.urls)),
    path("graphql/", csrf_exempt(graphql.PrivateGraphQLView.as_view()), name="graphql"),
]
