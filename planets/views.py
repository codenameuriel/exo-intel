from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Planet, StarSystem, Star
from .serializers import PlanetSerializer, StarSystemSerializer, StarSerializer
from .filters import PlanetFilter

class PlanetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows planets to be viewed or edited.
    """
    queryset = Planet.objects.select_related('host_star', 'discovery').order_by('name')
    serializer_class = PlanetSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'host_star__name']
    filterset_class = PlanetFilter

class StarSystemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows star systems to be viewed.
    """
    queryset = StarSystem.objects.all().order_by('name')
    serializer_class = StarSystemSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['num_stars', 'num_planets']

class StarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows stars to be viewed.
    """
    queryset = Star.objects.select_related('system').order_by('name')
    serializer_class = StarSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'system__name']
    filterset_fields = ['spect_type', 'system__name']

def planets(request):
    """
    A view to display a list of all planets in the database
    """
    planets = Planet.objects.select_related('host_star').order_by('name')
    context = {
        'planets': planets
    }

    return render(request, 'planets/planets.html', context)