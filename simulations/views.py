from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic
from planets.models import StarSystem
from tasks.tasks import travel_time_simulation_task

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
        system_id = request.data.get("star_system_id")
        speed_percentage = request.data.get("speed_percentage")

        if not system_id or not speed_percentage:
            return Response(
                {"error": "Both 'star_system_id' and 'speed_percentage' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            system_id = int(system_id)
            speed_percentage = float(speed_percentage)
            if not (0 < speed_percentage <= 100):
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {
                    "error": "'star_system_id' must be an integer and 'speed_percentage' must be a valid number between 1 and 100."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not StarSystem.objects.filter(id=system_id).exists():
            return Response(
                {"error": f"StarSystem with id {system_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        task = travel_time_simulation_task.delay(system_id, speed_percentage)

        response_data = {
            "message": "Simulation task has been started.",
            "task_id": task.id,
        }

        return Response(response_data, status=status.HTTP_202_ACCEPTED)