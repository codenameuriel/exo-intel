from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = "portal"

urlpatterns = [
    path("dashboard/", views.PortalDashboardView.as_view(), name="dashboard"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="portal/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("graphql/", csrf_exempt(views.PrivateGraphQLView.as_view()), name="graphql"),
]
