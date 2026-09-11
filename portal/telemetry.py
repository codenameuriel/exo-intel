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
class DashboardTelemetry:
    simulations_total: int
    simulations_today: int
    pending: int
    successful: int
    failed: int
    failures_today: int
    active_api_keys: int
    last_completed_at: datetime | None
    last_completed_type: str | None


def get_dashboard_telemetry(
    user: User,
    *,
    active_api_keys: int | None = None,
) -> DashboardTelemetry:
    """Return user-scoped operational metrics for the portal dashboard."""

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

    if active_api_keys is None:
        active_api_keys = APIKey.objects.filter(user=user).count()

    return DashboardTelemetry(
        **counts,
        active_api_keys=active_api_keys,
        last_completed_at=(last_completed or {}).get("completed_at"),
        last_completed_type=(last_completed or {}).get("simulation_type"),
    )
