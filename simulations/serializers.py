from rest_framework import serializers

from simulations.models import SimulationRun


class SimulationRunSerializer(serializers.ModelSerializer):
    """
    Serializer for the SimulationRun model.
    """

    user = serializers.StringRelatedField()

    class Meta:
        model = SimulationRun
        fields = [
            "id",
            "user",
            "status",
            "simulation_type",
            "result",
            "input_parameters",
            "created_at",
            "completed_at",
        ]


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
