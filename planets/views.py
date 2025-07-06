from django.shortcuts import render
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F, Case, When, Value, FloatField, IntegerField, Q, ExpressionWrapper
from django.db.models.functions import Abs, Round
from .models import Planet, StarSystem, Star
from .serializers import PlanetSerializer, StarSystemSerializer, StarSerializer
from .filters import PlanetFilter

class PlanetViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows planets to be viewed or edited.
    """
    serializer_class = PlanetSerializer
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'host_star__name']
    filterset_class = PlanetFilter
    ordering_fields = ['habitability_score', 'mass_earth', 'radius_earth', 'orbital_period']

    def get_queryset(self):
        # Database-level calculation

        # ideal temperature is earth-like (around 255 K)
        # for every 5 degrees off, subtract a point from 100 score
        density = ExpressionWrapper(
            F('mass_earth') / (F('radius_earth') ** 3),
            output_field=FloatField()
        )
        annotated_queryset = Planet.objects.annotate(density=density)

        density_score = Case(
            When(density__gte=0.75, then=Value(100.0)),
            When(density__gte=0.5, then=Value(50.0)),
            default=Value(0.0),
            output_field=FloatField()
        )
        # 60% temperature, 40% density
        temp_score = 100.0 - (Abs(F('equilibrium_temperature') - 255) / 5.0)
        habitability_score = (temp_score * 0.6) + (density_score * 0.4)

        # explicitly handle NULLs
        # calculations are performed only when field values are not NULL
        annotated_queryset = annotated_queryset.annotate(
            habitability_score=Case(
                When(
                    Q(equilibrium_temperature__isnull=False) &
                    Q(mass_earth__isnull=False) &
                    Q(radius_earth__isnull=False) &
                    Q(radius_earth__gt=0),
                    then=Round(habitability_score)
                ),
                default=Value(None),
                output_field=IntegerField()
            )
        ).select_related('host_star', 'discovery').order_by('name')

        return annotated_queryset

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