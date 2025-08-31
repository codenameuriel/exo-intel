from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import status, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic
from simulations.serializers import (
    SeasonalTempInputSerializer,
    SimulationRunSerializer,
    StarLifetimeInputSerializer,
    TidalLockingInputSerializer,
    TravelTimeInputSerializer,
)
from tasks.tasks import run_simulation_task
from .models import SimulationRun


@extend_schema(
    summary="[INTERNAL] Get the user's history of simulation runs.",
    description="**Warning:** This is an internal endpoint. "
                "It is documented here for informational purposes. Direct use is not recommended."
)
class SimulationHistoryView(ListAPIView):
    """
    A read-only view for simulation history.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = False

    serializer_class = SimulationRunSerializer

    # disable throttling
    throttle_classes = []

    def get_queryset(self):
        return SimulationRun.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )


@extend_schema(
    summary="[INTERNAL] Run a simulation.",
    description="**Warning:** This is an internal endpoint. "
                "It is documented here for informational purposes. Direct use is not recommended.",
    responses={
        202: OpenApiResponse(
            response=inline_serializer(
                name='SimulationRunResponse',
                fields={
                    'message': serializers.CharField(help_text='A message indicating that task has been started.'),
                    'task_id': serializers.CharField(help_text='The unique ID of the Celery task.')
                }
            )
        )
    }
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

        task = run_simulation_task.delay(
            user_id=request.user.id,
            simulation_type=SimulationRun.SimulationType.TRAVEL_TIME,
            input_parameters=serializer.validated_data,
        )

        return Response(
            {
                "message": "Simulation task has been started.",
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


@extend_schema(
    summary="[INTERNAL] Run a simulation.",
    description="**Warning:** This is an internal endpoint. "
                "It is documented here for informational purposes. Direct use is not recommended.",
    responses={
        202: OpenApiResponse(
            response=inline_serializer(
                name='SimulationRunResponse',
                fields={
                    'message': serializers.CharField(help_text='A message indicating that task has been started.'),
                    'task_id': serializers.CharField(help_text='The unique ID of the Celery task.')
                }
            )
        )
    }
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

        task = run_simulation_task.delay(
            user_id=request.user.id,
            simulation_type="SEASONAL_TEMPS",
            input_parameters=serializer.validated_data,
        )

        return Response(
            {
                "message": "Simulation task has been started.",
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


@extend_schema(
    summary="[INTERNAL] Run a simulation.",
    description="**Warning:** This is an internal endpoint. "
                "It is documented here for informational purposes. Direct use is not recommended.",
    responses={
        202: OpenApiResponse(
            response=inline_serializer(
                name='SimulationRunResponse',
                fields={
                    'message': serializers.CharField(help_text='A message indicating that task has been started.'),
                    'task_id': serializers.CharField(help_text='The unique ID of the Celery task.')
                }
            )
        )
    }
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
        serializer = TidalLockingInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = run_simulation_task.delay(
            user_id=request.user.id,
            simulation_type=SimulationRun.SimulationType.TIDAL_LOCKING,
            input_parameters=serializer.validated_data,
        )

        return Response(
            {
                "message": "Simulation task has been started.",
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


@extend_schema(
    summary="[INTERNAL] Run a simulation.",
    description="**Warning:** This is an internal endpoint. "
                "It is documented here for informational purposes. Direct use is not recommended.",
    responses={
        202: OpenApiResponse(
            response=inline_serializer(
                name='SimulationRunResponse',
                fields={
                    'message': serializers.CharField(help_text='A message indicating that task has been started.'),
                    'task_id': serializers.CharField(help_text='The unique ID of the Celery task.')
                }
            )
        )
    }
)
class StarLifetimeSimulationView(APIView):
    """
    An "action" API endpoint to estimate the lifetime of a star.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = False

    def post(self, request, *args, **kwargs):
        """
        Handles POST request to run the simulation.
        """

        serializer = StarLifetimeInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = run_simulation_task.delay(
            user_id=request.user.id,
            simulation_type=SimulationRun.SimulationType.STAR_LIFETIME,
            input_parameters=serializer.validated_data,
        )

        return Response(
            {
                "message": "Simulation task has been started.",
                "task_id": task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )
