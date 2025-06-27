from django.shortcuts import render
from rest_framework import viewsets
from .models import Planet, StarSystem, Star
from .serializers import PlanetSerializer, StarSystemSerializer, StarSerializer

class PlanetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows planets to be viewed or edited.
    """
    queryset = Planet.objects.select_related('host_star').order_by('name')
    serializer_class = PlanetSerializer

class StarSystemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows star systems to be viewed.
    """
    queryset = StarSystem.objects.all().order_by('name')
    serializer_class = StarSystemSerializer

class StarSerialier(viewsets.ModelViewSet):
    """
    API endpoint that allows stars to be viewed.
    """
    queryset = Star.objects.select_related('system').order_by('name')
    serializer_class = StarSerializer

def planets(request):
    """
    A view to display a list of all planets in the database
    """
    planets = Planet.objects.select_related('host_star').order_by('name')

    context = {
        'planets': planets
    }

    return render(request, 'planets/planets.html', context)