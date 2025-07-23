from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic
from simulations.serializers import (
    TravelTimeInputSerializer,
    SeasonalTempInputSerializer,
    TidalLockingInputSerializer,
)
from tasks.tasks import (
    travel_time_simulation_task,
    seasonal_temps_simulation_task,
    tidal_locking_simulation_task,
)


class TravelTimeSimulationView(APIView):
    """
    An "action" API endpoint to calculate the travel time to a star system.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = False

    def post(self, request, *args, **kwargs):
        """
        Handles POST request to run the simulation.
        """
        serializer = TravelTimeInputSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        task = travel_time_simulation_task.delay(**serializer.validated_data)

        return Response(
            {
                "message": "Simulation task has been started.",
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class SeasonalTempsSimulationView(APIView):
    """
    An "action" API endpoint to calculate the seasonal temperatures for a planet.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = False

    def post(self, request, *args, **kwargs):
        """
        Handles POST request to run the simulation.
        """
        serializer = SeasonalTempInputSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        task = seasonal_temps_simulation_task.delay(**serializer.validated_data)

        return Response(
            {
                "message": "Simulation task has been started.",
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class TidalLockingSimulationView(APIView):
    """
    An "action" API endpoint to estimate the probability that a planet is tidally locked.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = False

    def post(self, request, *args, **kwargs):
        """
        Handles POST request to run the simulation.
        """
        print("request.data", request.data)
        serializer = TidalLockingInputSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        print("serializer.validated_data", serializer.validated_data)

        task = tidal_locking_simulation_task.delay(**serializer.validated_data)

        return Response(
            {
                "message": "Simulation task has been started.",
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )
