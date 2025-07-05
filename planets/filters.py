from django_filters import rest_framework as filters
from django.db.models import F, Case, When, Value, FloatField, IntegerField, Q, ExpressionWrapper
from django.db.models.functions import Abs, Round
from .models import Planet

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
        method='filter_by_habitability_score',
    )

    class Meta:
        model = Planet
        fields = {
            'discovery__method': ['exact'],
            'discovery__locale': ['exact'],
        }

    def filter_by_habitability_score(self, queryset, name, value):
        """
        Custom filter method for filtering by habitability score.
        """

        # Database-level calculation

        # ideal temperature is earth-like (around 255 K)
        # for every 5 degrees off, subtract a point from 100 score
        density = ExpressionWrapper(
            F('mass_earth') / (F('radius_earth') ** 3),
            output_field=FloatField()
        )
        annotated_queryset = queryset.annotate(density=density)

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
        )

        if value.start is not None:
            annotated_queryset = annotated_queryset.filter(habitability_score__gte=value.start)
        if value.stop is not None:
            annotated_queryset = annotated_queryset.filter(habitability_score__lte=value.stop)

        return annotated_queryset