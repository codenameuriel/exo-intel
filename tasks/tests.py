from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from simulations.models import SimulationRun
from tasks.tasks import SIMULATION_DISPATCHER, run_simulation_task


class SimulationTaskTests(TestCase):
    @patch("tasks.tasks.time.sleep", return_value=None)
    def test_unexpected_simulation_error_is_persisted_as_failure(self, _mock_sleep):
        user = User.objects.create_user(username="operator", password="test-pass")

        def explode(**_kwargs):
            raise AttributeError("unexpected engine failure")

        with patch.dict(
            SIMULATION_DISPATCHER,
            {SimulationRun.SimulationType.TRAVEL_TIME: explode},
        ):
            result = run_simulation_task.apply(
                args=[
                    user.pk,
                    SimulationRun.SimulationType.TRAVEL_TIME,
                    {"star_system_id": 1, "speed_percentage": 50},
                ],
                task_id="unexpected-error-task",
            )

        self.assertTrue(result.failed())

        run = SimulationRun.objects.get(task_id="unexpected-error-task")
        self.assertEqual(run.status, SimulationRun.Status.FAILURE)
        self.assertEqual(
            run.result,
            {"error": "An unexpected error occurred while running the simulation."},
        )
        self.assertIsNotNone(run.completed_at)
