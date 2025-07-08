from django.db import models
from django.db.models import F, Case, When, Value, FloatField, IntegerField, Q, ExpressionWrapper
from django.db.models.functions import Abs, Round

class PlanetQuerySet(models.QuerySet):
    """
    A custom queryset for the Planet model with annotations.
    """
    def with_habitability(self):
        """
        Annotates each planet in the queryset with a calculated habitability score.
        """

        # Database-level calculation

        density = ExpressionWrapper(
            F('mass_earth') / (F('radius_earth') ** 3),
            output_field=FloatField()
        )

        queryset_with_density = self.annotate(density=density)

        density_score = Case(
            When(density__gte=0.75, then=Value(100.0)),
            When(density__gte=0.5, then=Value(50.0)),
            default=Value(0.0),
            output_field=FloatField()
        )
        # ideal temperature is earth-like (around 255 K)
        # for every 5 degrees off, subtract a point from 100 score
        temp_score = 100.0 - (Abs(F('equilibrium_temperature') - 255) / 5.0)
        # 60% temperature, 40% density
        habitability_score = (temp_score * 0.6) + (density_score * 0.4)

        # explicitly handle NULLs
        # calculations are performed only when field values are not NULL
        return queryset_with_density.annotate(
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

class PlanetManager(models.Manager):
    """
    A custom manager for the Planet model.
    """
    def get_queryset(self):
        return PlanetQuerySet(self.model, using=self._db)

    def with_habitability(self):
        """
        A convenience method to access the custom queryset method.
        """
        return self.get_queryset().with_habitability()