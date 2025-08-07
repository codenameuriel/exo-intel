from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import APIKeyDeleteView, SignUpView

app_name = "portal"

urlpatterns = [
    path("dashboard/", views.PortalDashboardView.as_view(), name="dashboard"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="portal/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "api-key/delete/<int:pk>/",
        APIKeyDeleteView.as_view(),
        name="api-key-delete",
    ),
]
