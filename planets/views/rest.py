from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.authentication import SessionAuthentication
from rest_framework.viewsets import ReadOnlyModelViewSet

from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic
from planets.filters import PlanetFilter
from planets.models import Planet, Star, StarSystem
from planets.serializers import (PlanetSerializer, StarSerializer,
                                 StarSystemSerializer)


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
