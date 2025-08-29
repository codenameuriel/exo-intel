"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


def health(_request):
    return HttpResponse("ok", content_type="text/plain")


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="portal:login"), name="home"),
    path("health/", health),
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    path("api/", include("api.urls")),
    path("portal/", include("portal.urls")),
    path("tasks/", include("tasks.urls")),
    path("simulations/", include("simulations.urls")),
    path(
        "api/schema/",
        login_required(SpectacularAPIView.as_view()),
        name="schema"
    ),
    path(
        "api/docs/",
        login_required(SpectacularSwaggerView.as_view(url_name="schema")),
        name="swagger-ui"
    ),
    path(
        "api/redoc/",
        login_required(SpectacularRedocView.as_view(url_name="schema")),
        name="redoc"
    ),
]
