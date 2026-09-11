from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from api_keys.models import APIKey
from portal.telemetry import get_dashboard_telemetry
from simulations.models import SimulationRun

User = get_user_model()


class DashboardTelemetryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="operator", password="test-pass")
        self.other_user = User.objects.create_user(
            username="other-operator",
            password="test-pass",
        )

    def create_run(
        self,
        *,
        user=None,
        task_id: str,
        status: str,
        simulation_type: str = SimulationRun.SimulationType.TRAVEL_TIME,
        completed_at=None,
    ) -> SimulationRun:
        return SimulationRun.objects.create(
            user=user or self.user,
            task_id=task_id,
            status=status,
            simulation_type=simulation_type,
            completed_at=completed_at,
        )

    def test_telemetry_is_user_scoped_and_reports_real_status_counts(self):
        now = timezone.now()
        self.create_run(
            task_id="pending-1",
            status=SimulationRun.Status.PENDING,
        )
        self.create_run(
            task_id="success-1",
            status=SimulationRun.Status.SUCCESS,
            simulation_type=SimulationRun.SimulationType.STAR_LIFETIME,
            completed_at=now - timedelta(minutes=10),
        )
        self.create_run(
            task_id="failure-1",
            status=SimulationRun.Status.FAILURE,
            completed_at=now - timedelta(minutes=5),
        )
        self.create_run(
            user=self.other_user,
            task_id="other-success",
            status=SimulationRun.Status.SUCCESS,
            completed_at=now,
        )

        APIKey.objects.create(user=self.user, name="Primary")
        APIKey.objects.create(user=self.user, name="Secondary")
        APIKey.objects.create(user=self.other_user, name="Other")

        telemetry = get_dashboard_telemetry(self.user)

        self.assertEqual(telemetry.simulations_total, 3)
        self.assertEqual(telemetry.simulations_today, 3)
        self.assertEqual(telemetry.pending, 1)
        self.assertEqual(telemetry.successful, 1)
        self.assertEqual(telemetry.failed, 1)
        self.assertEqual(telemetry.failures_today, 1)
        self.assertEqual(telemetry.active_api_keys, 2)
        self.assertEqual(telemetry.last_completed_at, now - timedelta(minutes=10))
        self.assertEqual(
            telemetry.last_completed_type,
            SimulationRun.SimulationType.STAR_LIFETIME,
        )

    def test_dashboard_exposes_telemetry_without_extra_api_key_count_query(self):
        APIKey.objects.create(user=self.user, name="Primary")
        self.create_run(
            task_id="pending-dashboard",
            status=SimulationRun.Status.PENDING,
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("portal:dashboard"))

        self.assertEqual(response.status_code, 200)
        telemetry = response.context["telemetry"]
        self.assertEqual(telemetry.active_api_keys, 1)
        self.assertEqual(telemetry.simulations_total, 1)
        self.assertEqual(telemetry.pending, 1)
        self.assertEqual(response.context["api_key_count"], 1)
