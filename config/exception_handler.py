from rest_framework.exceptions import (NotAuthenticated, PermissionDenied,
                                       ValidationError)
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    A custom exception handler for all DRF views.

    This function intercepts any exception and formats it into
    a consistent structure.
    """

    error_response = exception_handler(exc, context)

    if error_response is not None:
        error_data = {
            "success": False,
            "code": "generic_error",
            "message": "An error occurred.",
            "details": error_response.data,
        }

        if isinstance(exc, ValidationError):
            error_data["code"] = "validation_error"
            error_data["message"] = "Invalid input provided."
        elif isinstance(exc, NotAuthenticated):
            error_data["code"] = "authentication_error"
            error_data["message"] = "Authentication credentials were not provided."
        elif isinstance(exc, PermissionDenied):
            error_data["code"] = "permission_error"
            error_data["message"] = "You do not have permission to perform this action."

        error_response.data = error_data

    return error_response
