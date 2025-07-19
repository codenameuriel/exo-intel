from django.urls import path
from .views import TaskStatusView

app_name = "tasks"

urlpatterns = [
    path(
        "task-status/<str:task_id>/",
        TaskStatusView.as_view(),
        name="task-status"
    ),
]