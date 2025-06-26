from django.shortcuts import render
from .models import Planet

def planets(request):
    """
    A view to display a list of all planets in the database
    """
    planets = Planet.objects.select_related('host_star').order_by('name')

    context = {
        'planets': planets
    }

    return render(request, 'planets/planets.html', context)