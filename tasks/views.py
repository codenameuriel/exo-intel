from celery.result import AsyncResult
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import status, serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic


@extend_schema(
    summary="[INTERNAL] Get the status of a background Celery task from the Celery result backend.",
    description="**Warning:** This is an internal endpoint. "
                "It is documented here for informational purposes. Direct use is not recommended.",
    responses={
        200: OpenApiResponse(
            description="The current result of the task.",
            response=inline_serializer(
                name='TaskStatusResponse',
                fields={
                    'task_id': serializers.CharField(help_text='The unique ID of the Celery task.'),
                    'status': serializers.CharField(help_text='The current status of the task.'),
                    'result': serializers.JSONField(
                        help_text='Contains the simulation result on SUCCESS or an error object on FAILURE.'),
                },
            )
        ),
    },
)
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
