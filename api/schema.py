import graphene
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import DjangoObjectType

from .filters import PlanetFilter, StarFilter, StarSystemFilter
from .models import Planet, PlanetDiscovery, Star, StarSystem


class SpectralTypeEnum(graphene.Enum):
    O = "O"
    B = "B"
    A = "A"
    F = "F"
    G = "G"
    K = "K"
    M = "M"


class CustomConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()

    def resolve_total_count(self, info, **kwargs):
        return self.iterable.count()


class StarSystemType(DjangoObjectType):
    stars = graphene.List(graphene.NonNull(lambda: StarType))

    class Meta:
        model = StarSystem
        fields = ("id", "name", "distance_parsecs", "num_moons", "num_planets", "num_stars")
        interfaces = (graphene.relay.Node,)
        connection_class = CustomConnection

    def resolve_stars(self, info):
        return self.star_set.all()

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.prefetch_related("star_set")


class StarType(DjangoObjectType):
    planets = graphene.List(graphene.NonNull(lambda: PlanetType))

    class Meta:
        model = Star
        fields = ("id", "name", "mass_sun", "radius_sun", "luminosity_sun", "effective_temperature_k", "age_gya",
                  "spectral_type")
        interfaces = (graphene.relay.Node,)
        connection_class = CustomConnection

    def resolve_planets(self, info):
        return self.planet_set.all()

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset.prefetch_related("planet_set")


class PlanetDiscoveryType(DjangoObjectType):
    class Meta:
        model = PlanetDiscovery


class PlanetType(DjangoObjectType):
    # calculated field
    habitability_score = graphene.Int()

    class Meta:
        model = Planet
        fields = ("id", "name", "orbital_period_days", "radius_earth", "mass_earth", "equilibrium_temperature_k",
                  "semi_major_axis_au", "insolation_flux_earth", "orbital_eccentricity")
        interfaces = (graphene.relay.Node,)
        connection_class = CustomConnection

    def resolve_habitability_score(self, info):
        return getattr(self, "habitability_score", None)


class Query(graphene.ObjectType):
    planet_by_name = graphene.Field(PlanetType, name=graphene.String())
    all_planets = DjangoFilterConnectionField(PlanetType, filterset_class=PlanetFilter)

    star_by_name = graphene.Field(StarType, name=graphene.String())
    all_stars = DjangoFilterConnectionField(StarType, filterset_class=StarFilter)

    star_system_by_name = graphene.Field(lambda: StarSystemType, name=graphene.String())
    all_star_systems = DjangoFilterConnectionField(StarSystemType, filterset_class=StarSystemFilter)

    def resolve_planet_by_name(self, info, name):
        return Planet.objects.filter(name=name).first()

    def resolve_star_by_name(self, info, name):
        return Star.objects.filter(name=name).first()

    def resolve_star_system_by_name(self, info, name):
        return StarSystem.objects.filter(name=name).first()


schema = graphene.Schema(query=Query)
