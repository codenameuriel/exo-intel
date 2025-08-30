from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse, inline_serializer
from graphene_django.views import GraphQLView
from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView

from api.parsers import GraphQLParser
from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic


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

    @extend_schema(
        description=(
                "Access this endpoint in a web browser to open the interactive GraphiQL IDE. "
                "This is the primary tool for exploring and testing the GraphQL schema."
        )
    )
    def get(self, request, *args, **kwargs):
        """
        Handles browser GET requests which are used to render the GraphiQL interface
        """
        self.check_permissions(request)
        return GraphQLView.as_view(graphiql=True)(request, *args, **kwargs)

    @extend_schema(
        description="Send GraphQL queries to this endpoint via a POST request.",
        request=inline_serializer(
            name='GraphQLRequest',
            fields={
                'query': serializers.CharField(help_text='The GraphQL query string.'),
            },
        ),
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='GraphQLResponse',
                    fields={
                        'data': serializers.DictField(help_text='The GraphQL result data.'),
                        'errors': serializers.ListField(
                            child=serializers.DictField(), help_text='Any errors encountered.'
                        ),
                    },
                ),
            )
        },
        examples=[
            OpenApiExample(
                'Sample request',
                value={"query": "query { allStars(first: 3) { edges { node { name } } } }"},
                request_only=True,
            ),
            OpenApiExample(
                'Sample response',
                value={
                    "data": {
                        "allStars": {
                            "edges": [
                                {"node": {"name": "Kepler-27"}},
                                {"node": {"name": "Kepler-633"}},
                                {"node": {"name": "Kepler-1063"}},
                            ]
                        }
                    }
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        """
        Handles programmatic client POST requests which are used to simply return JSON.
        """
        self.check_permissions(request)
        return GraphQLView.as_view()(request, *args, **kwargs)
