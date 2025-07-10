from rest_framework import permissions, exceptions


class IsAuthenticatedOrPublic(permissions.BasePermission):
    """
    Custom permission that implements a freemium model.
    - Allows anonymous users throttled access to views marked as public.
    - Requires a valid API key, or session for all other views.
    """

    def has_permission(self, request, view):
        # check if view being accessed has custom attribute that marks it as public
        is_public_resource = getattr(view, "is_public_resource", False)
        if is_public_resource:
            return True

        # a user is authenticated either:
        # 1. if a valid api key token is provided
        # 2. user signed in and a session was created
        return request.user and request.user.is_authenticated
