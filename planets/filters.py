from django_filters import rest_framework as filters
from django.db.models import F, Case, When, Value, FloatField, IntegerField, Q, ExpressionWrapper
from django.db.models.functions import Abs, Round
from .models import Planet

# Morgan-Keenan stellar classification
# hottest (O type) to coolest (M type)
SPECTRAL_TYPE_CHOICES = [
    ('O', 'O-type'),
    ('B', 'B-type'),
    ('A', 'A-type'),
    ('F', 'F-type'),
    ('G', 'G-type (Sun-like)'),
    ('K', 'K-type'),
    ('M', 'M-type (Red Dwarf'),
]

class PlanetFilter(filters.FilterSet):
    """
    Custom filterset for the Planet model.

    This filterset allows for advanced filtering on the 'habitability_score',
    which is a calculated field provided by the PlanetViewSet's queryset.
    """

    # This creates a filter that can be used with query parameters like:
    # ?habitability_score_min=80&habitability_score_max=100
    habitability_score = filters.RangeFilter(
        label="Habitability Score",
    )

    # ?radius_earth_max=1.5
    radius_earth = filters.RangeFilter(label='Radius (Earth Radii')
    # ?mass_earth_min=0.5&mass_earth_max=2.0
    mass_earth = filters.RangeFilter(label='Mass (Earth Masses')
    # ?orbital_period_min=365
    orbital_period = filters.RangeFilter(label='Orbital Period (Days)')

    # use host_star__spect_type__startswith to match the main letter (e.g., 'G' matches 'G2V')
    # ?host_star_type=G
    host_star_type = filters.ChoiceFilter(
        label="Host Star's Spectral Type",
        field_name='host_star__spect_type',
        lookup_expr='startswith',
        choices=SPECTRAL_TYPE_CHOICES
    )

    # ?ordering=habitability_score
    ordering = filters.OrderingFilter(
        fields=(
            ('habitability_score', 'habitability_score'),
            ('radius_earth', 'radius_earth'),
            ('mass_earth', 'mass_earth'),
            ('orbital_period', 'orbital_period'),
        )
    )

    class Meta:
        model = Planet
        fields = {
            'discovery__method': ['exact'],
            'discovery__locale': ['exact'],
        }