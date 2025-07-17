from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic
from planets.models import StarSystem
from planets.simulations import SimulationEngine


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
            speed_percentage = float(speed_percentage)
        except ValueError:
            return Response(
                {"error": "'speed_percentage' must be a valid number."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        star_system = get_object_or_404(StarSystem, pk=system_id)

        try:
            travel_time = SimulationEngine.calculate_travel_time(
                star_system, speed_percentage
            )
            if travel_time is None:
                return Response(
                    {
                        "error": "The travel time could not be calculated. The star system may be missing distance data"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response_data = {
            "star_system_name": star_system.name,
            "travel_speed_percentage_c": speed_percentage,
            "travel_time_years": travel_time,
        }

        return Response(response_data, status=status.HTTP_200_OK)
