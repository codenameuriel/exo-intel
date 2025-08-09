from django.urls import path

from .views import TaskStatusView

app_name = "tasks"

urlpatterns = [
    path("status/<str:task_id>/", TaskStatusView.as_view(), name="task-status"),
]
