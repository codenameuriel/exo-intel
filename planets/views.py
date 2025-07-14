from django.shortcuts import render
from rest_framework import filters
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Planet, StarSystem, Star
from .serializers import PlanetSerializer, StarSystemSerializer, StarSerializer
from .filters import PlanetFilter
from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic
from rest_framework.authentication import SessionAuthentication
from graphene_django.views import GraphQLView
from .parsers import GraphQLParser


class PlanetViewSet(ReadOnlyModelViewSet):
    """
    Read-only API endpoint for planets.
    This is the "freemium" resource.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = True

    queryset = (
        Planet.objects.with_habitability()
        .select_related("host_star", "discovery")
        .order_by("name")
    )
    serializer_class = PlanetSerializer
    filter_backends = [
        filters.SearchFilter,
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "host_star__name"]
    filterset_class = PlanetFilter
    ordering_fields = [
        "habitability_score",
        "mass_earth",
        "radius_earth",
        "orbital_period",
    ]


class StarSystemViewSet(ReadOnlyModelViewSet):
    """
    Read-only API endpoint for star systems.
    This a private resource.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = False

    queryset = StarSystem.objects.all().order_by("name")
    serializer_class = StarSystemSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name"]
    filterset_fields = ["num_stars", "num_planets"]


class StarViewSet(ReadOnlyModelViewSet):
    """
    Read-only API endpoint for stars.
    This is a private resource.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = False

    queryset = Star.objects.select_related("system").order_by("name")
    serializer_class = StarSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["name", "system__name"]
    filterset_fields = ["spect_type", "system__name"]


def planets(request):
    """
    A view to display a list of all planets in the database
    """
    planets = Planet.objects.select_related("host_star").order_by("name")
    context = {"planets": planets}

    return render(request, "planets/planets.html", context)


class PrivateGraphQLView(APIView):
    """
    A wrapper view that applies DRF's security to the GraphQL endpoint.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = False

    # overriding DRF APIView parser to prevent it from consuming the request body before it gets to the
    # GraphQLView, which solves the "cannot access body after reading" error.
    parser_classes = [GraphQLParser]

    def get(self, request, *args, **kwargs):
        """
        Handles browser GET requests which are used to render the GraphiQL interface
        """
        self.check_permissions(request)
        return GraphQLView.as_view(graphiql=True)(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles programmatic client POST requests which are used to simply return JSON.
        """
        self.check_permissions(request)
        return GraphQLView.as_view()(request, *args, **kwargs)
