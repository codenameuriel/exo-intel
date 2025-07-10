from rest_framework import authentication
from rest_framework import exceptions
from .models import APIKey


class APIKeyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION")
        # allow the request to continue to the SessionAuthentication
        if not header:
            return None

        try:
            prefix, key = header.split()
            if prefix.lower() != "api-key":
                raise exceptions.AuthenticationFailed(
                    'Invalid API key prefix. Must be "Api-Key".'
                )
        except ValueError:
            raise exceptions.AuthenticationFailed(
                "Invalid Authorization header format."
            )

        try:
            api_key = APIKey.objects.select_related("user").get(key=key)
            user = api_key.user
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid API Key provided.")

        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                "User is inactive or has been deleted."
            )

        # sets api_key token on the request's auth
        return user, api_key

    def authenticate_header(self, request):
        """
        Returns a string to be used in the 'WWW-Authenticate' header
        for a 401 Unauthorized response.
        The browsable API renderer looks for this method to determine
        rendering the "Authorize" button and header input box.
        """
        return "Api-Key"
