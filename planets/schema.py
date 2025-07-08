import graphene
from graphene_django.types import DjangoObjectType
from .models import Planet, PlanetDiscovery, Star, StarSystem

class SpectralTypeEnum(graphene.Enum):
    O = "O"
    B = "B"
    A = "A"
    F = "F"
    G = "G"
    K = "K"
    M = "M"

class StarSystemType(DjangoObjectType):
    class Meta:
        model = StarSystem
        fields = "__all__"

class StarType(DjangoObjectType):
    class Meta:
        model = Star
        fields = "__all__"

class PlanetDiscoveryType(DjangoObjectType):
    class Meta:
        model = PlanetDiscovery
        fields = "__all__"

class PlanetType(DjangoObjectType):
    # calculated field
    habitability_score = graphene.Int()

    class Meta:
        model = Planet
        fields = "__all__"

    def resolve_habitability_score(self, info):
        return getattr(self, 'habitability_score', None)

class Query(graphene.ObjectType):
    # entry points for API
    all_planets = graphene.List(
        PlanetType,
        discovery_method=graphene.String(description="Filter by discovery method (e.g., 'Transit')"),
        discovery_locale=graphene.String(description="Filter by discovery locale (e.g., 'Space')"),
        host_star_type=graphene.Argument(SpectralTypeEnum, description="Filter by host star's spectral type (e.g., G for Sun-like)"),
        radius_earth_min=graphene.Float(description="Minimum planet radius in Earth radii"),
        radius_earth_max=graphene.Float(description="Maximum planet radius in Eath radii"),
        mass_earth_min=graphene.Float(description="Minimum planet mass in Earth masses"),
        mass_earth_max=graphene.Float(description="Maximum planet mass in Earth masses"),
        orbital_period_min=graphene.Float(description="Minimum orbital period in days"),
        orbital_period_max=graphene.Float(description="Maximum orbital period in days"),
        habitability_score_min=graphene.Argument(graphene.Int),
        habitability_score_max=graphene.Argument(graphene.Int),
    )
    all_stars = graphene.List(StarType)

    planet_by_name = graphene.Field(PlanetType, name=graphene.String(required=True))

    def resolve_all_planets(self, info, **kwargs):
        queryset = Planet.objects.with_habitability()

        if discovery_method := kwargs.get('discovery_method'):
            queryset = queryset.filter(discovery__method__iexact=discovery_method)
        if discovery_locale := kwargs.get('discovery_locale'):
            queryset = queryset.filter(discovery__locale__iexact=discovery_locale)

        if host_star_type := kwargs.get('host_star_type'):
            queryset = queryset.filter(host_star__spect_type__startswith=host_star_type.value)

        if radius_earth_min := kwargs.get('radius_earth_min'):
            queryset = queryset.filter(radius_earth__gte=radius_earth_min)
        if radius_earth_max := kwargs.get('radius_earth_max'):
            queryset = queryset.filter(radius_earth__lte=radius_earth_max)

        if mass_earth_min := kwargs.get('mass_earth_min'):
            queryset = queryset.filter(mass_earth__gte=mass_earth_min)
        if mass_earth_max := kwargs.get('mass_earth_max'):
            queryset = queryset.filter(mass_earth__lte=mass_earth_max)

        if orbital_period_min := kwargs.get('orbital_period_min'):
            queryset = queryset.filter(orbital_period__gte=orbital_period_min)
        if orbital_period_max := kwargs.get('orbital_period_max'):
            queryset = queryset.filter(orbital_period__lte=orbital_period_max)

        if score_min := kwargs.get('habitability_score_min'):
            queryset = queryset.filter(habitability_score__gte=score_min)
        if score_max := kwargs.get('habitability_score_max'):
            queryset = queryset.filter(habitability_score__lte=score_max)

        return queryset.select_related('host_star', 'discovery').order_by('name')


    def resolve_all_stars(self, info, **kwargs):
        return Star.objects.select_related('system').all()

    def resolve_planet_by_name(self, info, **kwargs):
        try:
            return Planet.objects.get(name=kwargs['name'])
        except Planet.DoesNotExist:
            return None