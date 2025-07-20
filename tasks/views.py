from celery.result import AsyncResult
from celery.exceptions import NotRegistered
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic


class TaskStatusView(APIView):
    """
    An API endpoint to check the status of a background task.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = False

    def get(self, request, task_id, *args, **kwargs):
        """
        Handles GET request to check the status of a background task.
        """

        # get task state and result from Celery result backend
        task_result = AsyncResult(task_id)

        response_data = {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None,
        }

        return Response(response_data, status=status.HTTP_200_OK)
