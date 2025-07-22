from rest_framework import serializers
from planets.models import StarSystem, Planet


class TravelTimeInputSerializer(serializers.Serializer):
    """
    A class to serialize input data for validation
    """

    star_system_id = serializers.IntegerField()
    speed_percentage = serializers.FloatField(min_value=1, max_value=100)

    def validate_star_system_id(self, value):
        if not StarSystem.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"StarSystem with id {value} not found.")


class SeasonalTempInputSerializer(serializers.Serializer):
    """
    A class to serialize input data for validation
    """

    planet_id = serializers.IntegerField()

    def validate_planet_id(self, value):
        if not Planet.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Planet with id {value} not found.")
