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
    class Meta:
        model = StarSystem
        fields = "__all__"
        interfaces = (graphene.relay.Node,)
        connection_class = CustomConnection


class StarType(DjangoObjectType):
    class Meta:
        model = Star
        fields = "__all__"
        interfaces = (graphene.relay.Node,)
        connection_class = CustomConnection


class PlanetDiscoveryType(DjangoObjectType):
    class Meta:
        model = PlanetDiscovery


class PlanetType(DjangoObjectType):
    # calculated field
    habitability_score = graphene.Int()

    class Meta:
        model = Planet
        fields = "__all__"
        interfaces = (graphene.relay.Node,)
        connection_class = CustomConnection

    def resolve_habitability_score(self, info):
        return getattr(self, "habitability_score", None)


class Query(graphene.ObjectType):
    planet = graphene.relay.Node.Field(PlanetType)
    all_planets = DjangoFilterConnectionField(PlanetType, filterset_class=PlanetFilter)

    star = graphene.relay.Node.Field(StarType)
    all_stars = DjangoFilterConnectionField(StarType, filterset_class=StarFilter)

    star_system = graphene.relay.Node.Field(StarSystemType)
    all_star_systems = DjangoFilterConnectionField(StarSystemType, filterset_class=StarSystemFilter)


schema = graphene.Schema(query=Query)
