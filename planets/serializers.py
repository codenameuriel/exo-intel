from rest_framework import serializers
from .models import Planet, StarSystem, Star


class PlanetSerializer(serializers.ModelSerializer):
    """
    Serializer for the Planet model.
    """

    host_star = serializers.StringRelatedField()
    discovery = serializers.StringRelatedField()
    habitability_score = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = Planet
        fields = [
            "id",
            "name",
            "host_star",
            "mass_earth",
            "radius_earth",
            "orbital_period",
            "equilibrium_temperature",
            "discovery",
            "habitability_score",
        ]


class StarSystemSerializer(serializers.ModelSerializer):
    """
    Serializer for the StarSystem model.
    """

    class Meta:
        model = StarSystem
        fields = [
            "id",
            "name",
            "num_stars",
            "num_planets",
            "num_moons",
            "distance",
            "ra",
            "dec",
        ]


class StarSerializer(serializers.ModelSerializer):
    """
    Serializer for the Star model.
    """

    system = serializers.StringRelatedField()

    class Meta:
        model = Star
        fields = ["id", "name", "system", "spect_type", "mass", "radius", "temperature"]
