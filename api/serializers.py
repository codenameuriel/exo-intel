from rest_framework import serializers

from .models import Planet, Star, StarSystem


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
            "orbital_period_days",
            "equilibrium_temperature_k",
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
            "distance_parsecs",
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
        fields = ["id", "name", "system", "spectral_type", "mass_sun", "radius_sun", "effective_temperature_k"]
