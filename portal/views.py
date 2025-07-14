from graphene_django.views import GraphQLView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from api_keys.authentication import APIKeyAuthentication
from api_keys.permissions import IsAuthenticatedOrPublic


class PortalDashboardView(LoginRequiredMixin, TemplateView):
    """ "
    This view serves as the main landing page for a developer
    after they have successfully logged in.
    """

    template_name = "portal/dashboard.html"


class PrivateGraphQLView(APIView):
    """
    A wrapper view that applies DRF's security to the GraphQL endpoint.
    """

    authentication_classes = [APIKeyAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticatedOrPublic]

    is_public_resource = False

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests which are used by the GraphiQL interface.
        """
        self.check_permissions(request)
        return GraphQLView.as_view(graphiql=True)(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.check_permissions(request)
        return GraphQLView.as_view()(request, *args, **kwargs)
