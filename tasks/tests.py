from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

from simulations.models import SimulationRun
from tasks.tasks import (
    SIMULATION_DISPATCHER,
    reconcile_stale_simulation_runs,
    run_simulation_task,
)


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


@override_settings(SIMULATION_PENDING_TIMEOUT_SECONDS=120)
class StaleSimulationRunTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="operator", password="test-pass")

    def create_run(self, *, task_id, status=SimulationRun.Status.PENDING):
        return SimulationRun.objects.create(
            user=self.user,
            task_id=task_id,
            simulation_type=SimulationRun.SimulationType.TRAVEL_TIME,
            status=status,
        )

    def test_stale_pending_run_is_marked_timed_out(self):
        run = self.create_run(task_id="stale-pending")
        stale_created_at = timezone.now() - timedelta(minutes=3)
        SimulationRun.objects.filter(pk=run.pk).update(created_at=stale_created_at)

        updated_count = reconcile_stale_simulation_runs.run()

        self.assertEqual(updated_count, 1)
        run.refresh_from_db()
        self.assertEqual(run.status, SimulationRun.Status.TIMED_OUT)
        self.assertEqual(
            run.result,
            {"error": "Simulation timed out before completion."},
        )
        self.assertIsNotNone(run.completed_at)

    def test_recent_pending_run_remains_pending(self):
        run = self.create_run(task_id="recent-pending")

        updated_count = reconcile_stale_simulation_runs.run()

        self.assertEqual(updated_count, 0)
        run.refresh_from_db()
        self.assertEqual(run.status, SimulationRun.Status.PENDING)
        self.assertIsNone(run.completed_at)

    def test_terminal_runs_are_not_reconciled(self):
        completed_at = timezone.now() - timedelta(minutes=3)
        success = self.create_run(
            task_id="old-success",
            status=SimulationRun.Status.SUCCESS,
        )
        failure = self.create_run(
            task_id="old-failure",
            status=SimulationRun.Status.FAILURE,
        )
        stale_created_at = timezone.now() - timedelta(minutes=5)
        SimulationRun.objects.filter(pk__in=[success.pk, failure.pk]).update(
            created_at=stale_created_at,
            completed_at=completed_at,
        )

        updated_count = reconcile_stale_simulation_runs.run()

        self.assertEqual(updated_count, 0)
        success.refresh_from_db()
        failure.refresh_from_db()
        self.assertEqual(success.status, SimulationRun.Status.SUCCESS)
        self.assertEqual(failure.status, SimulationRun.Status.FAILURE)
        self.assertEqual(success.completed_at, completed_at)
        self.assertEqual(failure.completed_at, completed_at)
