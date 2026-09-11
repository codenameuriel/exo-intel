from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone

from api_keys.models import APIKey
from simulations.models import SimulationRun

User = get_user_model()


@dataclass(frozen=True)
class PortalTelemetry:
    simulations_total: int
    simulations_today: int
    pending: int
    successful: int
    failed: int
    failures_today: int
    active_api_keys: int
    last_completed_at: datetime | None
    last_completed_type: str | None

    def as_dict(self) -> dict[str, int | str | datetime | None]:
        return {
            "simulations_total": self.simulations_total,
            "simulations_today": self.simulations_today,
            "pending": self.pending,
            "successful": self.successful,
            "failed": self.failed,
            "failures_today": self.failures_today,
            "active_api_keys": self.active_api_keys,
            "last_completed_at": self.last_completed_at,
            "last_completed_type": self.last_completed_type,
        }


def get_portal_telemetry(user: User) -> PortalTelemetry:
    """Return user-scoped operational metrics for the developer portal."""

    today = timezone.localdate()
    simulations = SimulationRun.objects.filter(user=user)

    counts = simulations.aggregate(
        simulations_total=Count("id"),
        simulations_today=Count("id", filter=Q(created_at__date=today)),
        pending=Count("id", filter=Q(status=SimulationRun.Status.PENDING)),
        successful=Count("id", filter=Q(status=SimulationRun.Status.SUCCESS)),
        failed=Count("id", filter=Q(status=SimulationRun.Status.FAILURE)),
        failures_today=Count(
            "id",
            filter=Q(
                status=SimulationRun.Status.FAILURE,
                created_at__date=today,
            ),
        ),
    )

    last_completed = (
        simulations.filter(
            status=SimulationRun.Status.SUCCESS,
            completed_at__isnull=False,
        )
        .order_by("-completed_at")
        .values("simulation_type", "completed_at")
        .first()
    )

    return PortalTelemetry(
        **counts,
        active_api_keys=APIKey.objects.filter(user=user).count(),
        last_completed_at=(last_completed or {}).get("completed_at"),
        last_completed_type=(last_completed or {}).get("simulation_type"),
    )
