from django.test import TestCase

from api.models import StarSystem
from simulations.engine import SimulationEngine
from simulations.exceptions import SimulationError


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
