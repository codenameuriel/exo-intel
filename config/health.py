import os

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from config.celery import app as celery_app

CELERY_HEALTH_TIMEOUT_SECONDS = 0.5


def check_database() -> dict[str, str]:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return {"status": "unavailable"}

    return {"status": "ok"}


def check_celery_worker() -> dict[str, int | str]:
    try:
        inspector = celery_app.control.inspect(timeout=CELERY_HEALTH_TIMEOUT_SECONDS)
        workers = inspector.ping() or {}
    except Exception:
        workers = {}

    if not workers:
        return {"status": "unavailable", "workers": 0}

    return {"status": "ok", "workers": len(workers)}


def get_environment() -> str:
    configured_environment = os.getenv("ENVIRONMENT")
    if configured_environment:
        return configured_environment

    settings_module = os.getenv("DJANGO_SETTINGS_MODULE", "")
    if settings_module:
        return settings_module.rsplit(".", maxsplit=1)[-1]

    return "unknown"


@require_GET
def health(request):
    database = check_database()
    celery_worker = check_celery_worker()
    checks = {
        "application": {"status": "ok"},
        "database": database,
        "celery_worker": celery_worker,
    }

    overall_status = (
        "ok"
        if all(check["status"] == "ok" for check in checks.values())
        else "degraded"
    )

    response = JsonResponse(
        {
            "status": overall_status,
            "service": "exo-intel",
            "version": settings.APP_VERSION,
            "environment": get_environment(),
            "checks": checks,
        }
    )
    response["Cache-Control"] = "no-store"
    return response
