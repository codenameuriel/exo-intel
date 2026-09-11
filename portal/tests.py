from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from config.health import check_celery_worker, check_database


class HealthEndpointTests(SimpleTestCase):
    @override_settings(APP_VERSION="9.9.9")
    @patch.dict("os.environ", {"ENVIRONMENT": "test"}, clear=False)
    @patch("config.health.check_celery_worker")
    @patch("config.health.check_database")
    def test_health_reports_healthy_dependencies(
        self,
        mock_database,
        mock_celery_worker,
    ):
        mock_database.return_value = {"status": "ok"}
        mock_celery_worker.return_value = {"status": "ok", "workers": 2}

        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "service": "exo-intel",
                "version": "9.9.9",
                "environment": "test",
                "checks": {
                    "application": {"status": "ok"},
                    "database": {"status": "ok"},
                    "celery_worker": {"status": "ok", "workers": 2},
                },
            },
        )

    @patch("config.health.check_celery_worker")
    @patch("config.health.check_database")
    def test_health_reports_degraded_without_failing_liveness(
        self,
        mock_database,
        mock_celery_worker,
    ):
        mock_database.return_value = {"status": "ok"}
        mock_celery_worker.return_value = {"status": "unavailable", "workers": 0}

        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "degraded")
        self.assertEqual(
            response.json()["checks"]["celery_worker"],
            {"status": "unavailable", "workers": 0},
        )

    def test_health_is_get_only(self):
        response = self.client.post(reverse("health"))

        self.assertEqual(response.status_code, 405)


class HealthCheckTests(TestCase):
    def test_database_check_uses_available_database_connection(self):
        result = check_database()

        self.assertEqual(result, {"status": "ok"})

    @patch("config.health.celery_app.control.inspect")
    def test_celery_check_counts_responsive_workers(self, mock_inspect):
        inspector = MagicMock()
        inspector.ping.return_value = {
            "celery@worker-1": {"ok": "pong"},
            "celery@worker-2": {"ok": "pong"},
        }
        mock_inspect.return_value = inspector

        result = check_celery_worker()

        self.assertEqual(result, {"status": "ok", "workers": 2})
        mock_inspect.assert_called_once()
