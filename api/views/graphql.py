from graphene_django.views import GraphQLView
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView

from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic
from api.parsers import GraphQLParser


class PrivateGraphQLView(APIView):
    """
    A wrapper view that applies DRF's security to the GraphQL endpoint.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]
    is_public_resource = False

    # overriding DRF APIView parser to prevent it from consuming the request body before it gets to the
    # GraphQLView, which solves the "cannot access body after reading" error.
    parser_classes = [GraphQLParser]

    def get(self, request, *args, **kwargs):
        """
        Handles browser GET requests which are used to render the GraphiQL interface
        """
        self.check_permissions(request)
        return GraphQLView.as_view(graphiql=True)(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles programmatic client POST requests which are used to simply return JSON.
        """
        self.check_permissions(request)
        return GraphQLView.as_view()(request, *args, **kwargs)
