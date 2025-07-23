from celery.result import AsyncResult
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

        result_data = None
        if task_result.ready():
            if task_result.failed():
                result_data = {
                    "error": True,
                    "message": str(task_result.result),
                }
            else:
                result_data = task_result.result

        response_data = {
            "task_id": task_id,
            "status": task_result.status,
            "result": result_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
