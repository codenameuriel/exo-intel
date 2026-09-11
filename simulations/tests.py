from django.contrib.auth.models import User
from django.test import TestCase

from api.models import StarSystem
from simulations.engine import SimulationEngine
from simulations.exceptions import SimulationError
from simulations.models import SimulationRun
from simulations.serializers import SimulationRunSerializer


class TravelTimeSimulationTests(TestCase):
    def test_calculates_travel_time_from_parsec_distance(self):
        star_system = StarSystem.objects.create(
            name="Test System",
            distance_parsecs=1.0,
        )

        result = SimulationEngine.calculate_travel_time(
            star_system_id=star_system.pk,
            speed_percentage=100,
        )

        self.assertEqual(result["star_system_name"], "Test System")
        self.assertEqual(result["travel_speed_percentage_c"], 100)
        self.assertEqual(result["travel_time_years"], 3.26)

    def test_rejects_star_system_without_distance(self):
        star_system = StarSystem.objects.create(name="Unknown Distance")

        with self.assertRaisesMessage(
            SimulationError,
            "Cannot calculate travel time: Star system is missing distance data.",
        ):
            SimulationEngine.calculate_travel_time(
                star_system_id=star_system.pk,
                speed_percentage=50,
            )


class SimulationRunSerializerTests(TestCase):
    def test_exposes_task_id_for_exact_client_tracking(self):
        user = User.objects.create_user(username="operator", password="test-pass")
        run = SimulationRun.objects.create(
            user=user,
            task_id="tracked-task-id",
            simulation_type=SimulationRun.SimulationType.TRAVEL_TIME,
        )

        data = SimulationRunSerializer(run).data

        self.assertEqual(data["task_id"], "tracked-task-id")
