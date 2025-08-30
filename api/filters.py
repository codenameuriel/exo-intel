from django_filters import rest_framework as filters

from .models import Planet, Star, StarSystem
from .widgets import LabeledRangeWidget

# Morgan-Keenan stellar classification
# hottest (O type) to coolest (M type)
SPECTRAL_TYPE_CHOICES = [
    ("O", "O-type"),
    ("B", "B-type"),
    ("A", "A-type"),
    ("F", "F-type"),
    ("G", "G-type (Sun-like)"),
    ("K", "K-type"),
    ("M", "M-type (Red Dwarf"),
]


class PlanetFilter(filters.FilterSet):
    """
    Custom filterset for the Planet model.

    This filterset allows for advanced filtering on the 'habitability_score',
    which is a calculated field provided by the PlanetViewSet's queryset.
    """

    # ensure consistent filtering results between REST and GraphQL
    discovery__year = filters.NumberFilter(
        field_name="discovery__year",
        lookup_expr="exact",
    )

    # This creates a filter that can be used with query parameters like:
    # ?habitability_score_min=80&habitability_score_max=100
    habitability_score = filters.RangeFilter(
        label="Habitability Score",
        widget=LabeledRangeWidget(
            min_placeholder="min score", max_placeholder="max score"
        ),
    )

    # ?radius_earth_max=1.5
    radius_earth = filters.RangeFilter(
        label="Radius (Earth Radii)",
        widget=LabeledRangeWidget(
            min_placeholder="min radius", max_placeholder="max radius"
        ),
    )
    # ?mass_earth_min=0.5&mass_earth_max=2.0
    mass_earth = filters.RangeFilter(
        label="Mass (Earth Masses)",
        widget=LabeledRangeWidget(
            min_placeholder="min mass", max_placeholder="max mass"
        ),
    )
    # ?orbital_period_min=365
    orbital_period = filters.RangeFilter(
        label="Orbital Period (Days)",
        widget=LabeledRangeWidget(
            min_placeholder="min period", max_placeholder="max period"
        ),
    )

    # use host_star__spect_type__startswith to match the main letter (e.g., 'G' matches 'G2V')
    # ?host_star_type=G
    host_star_type = filters.ChoiceFilter(
        label="Host Star's Spectral Type",
        field_name="host_star__spect_type",
        lookup_expr="startswith",
        choices=SPECTRAL_TYPE_CHOICES,
    )

    # ?ordering=habitability_score
    ordering = filters.OrderingFilter(
        fields=(
            ("habitability_score", "habitability_score"),
            ("radius_earth", "radius_earth"),
            ("mass_earth", "mass_earth"),
            ("orbital_period", "orbital_period"),
        )
    )

    class Meta:
        model = Planet
        fields = {
            "name": ["exact"],
            "host_star__name": ["exact"],
            # "discovery__year": ["exact"],
            "discovery__method": ["exact"],
            "discovery__locale": ["exact"],
        }


class StarFilter(filters.FilterSet):
    """
    Custom filterset for the Star model.
    """

    class Meta:
        model = Star
        fields = {
            "name": ["exact"],
        }


class StarSystemFilter(filters.FilterSet):
    """
    Custom filterset for the StarSystem model.
    """

    class Meta:
        model = StarSystem
        fields = {
            "name": ["exact"],
            "num_stars": ["exact"],
            "num_planets": ["exact"],
            "num_moons": ["exact"],
        }
