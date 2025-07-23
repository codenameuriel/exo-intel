from rest_framework import serializers


class TravelTimeInputSerializer(serializers.Serializer):
    """
    A class to serialize input data for validation
    """

    star_system_id = serializers.IntegerField()
    speed_percentage = serializers.FloatField(min_value=1, max_value=100)


class SeasonalTempInputSerializer(serializers.Serializer):
    """
    A class to serialize input data for validation
    """

    planet_id = serializers.IntegerField()


class TidalLockingInputSerializer(serializers.Serializer):
    """
    A class to serialize input data for validation
    """

    planet_id = serializers.IntegerField()


class StarLifetimeInputSerializer(serializers.Serializer):
    """
    A class to serialize input data for validation
    """

    star_id = serializers.IntegerField()
