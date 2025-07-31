from django.db import models
from django.conf import settings


class SimulationRun(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILURE = "FAILURE", "Failure"

    class SimulationType(models.TextChoices):
        TRAVEL_TIME = "TRAVEL_TIME", "Travel Time"
        SEASONAL_TEMPS = "SEASONAL_TEMPS", "Seasonal Temperatures"
        TIDAL_LOCKING = "TIDAL_LOCKING", "Tidal Locking"
        STAR_LIFETIME = "STAR_LIFETIME", "Star Lifetime"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task_id = models.CharField(max_length=255, unique=True)
    simulation_type = models.CharField(max_length=50, choices=SimulationType.choices)
    input_parameters = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.simulation_type} ({self.task_id}) for {self.user.username}"
