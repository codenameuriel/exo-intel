from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from api_keys.models import APIKey
from planets.models import StarSystem, Planet


class PortalDashboardView(LoginRequiredMixin, View):
    """
    This view serves as the main landing page for a developer
    after they have successfully logged in.
    """

    template_name = "portal/dashboard.html"

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests. Fetches the user's existing API keys
        and renders the dashboard template with them.
        """
        api_keys = APIKey.objects.filter(user=request.user)

        # simulation data models
        star_systems = StarSystem.objects.filter(distance__isnull=False).order_by(
            "name"
        )
        planets = (
            Planet.objects.filter(
                Q(host_star__luminosity__isnull=False)
                | (
                    Q(host_star__radius__isnull=False)
                    & Q(host_star__temperature__isnull=False)
                ),
                semi_major_axis__isnull=False,
                orbital_eccentricity__isnull=False,
            )
            .select_related("host_star")
            .order_by("name")
            .distinct()
        )

        context = {
            "api_keys": api_keys,
            "api_key_count": api_keys.count(),
            "star_systems": star_systems,
            "planets": planets,
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests from the api key generation form.
        Creates a new API key for the logged-in user.
        """
        if APIKey.objects.filter(user=request.user).count() >= 3:
            messages.error(request, "You have reached the API key limit of 3")
            return redirect("portal:dashboard")

        key_name = request.POST.get("key_name")
        if key_name:
            APIKey.objects.create(user=request.user, name=key_name)
            messages.success(request, f"Successfully created new API key: '{key_name}'")
        else:
            messages.error(request, "API key name cannot be empty")

        return redirect("portal:dashboard")


class APIKeyDeleteView(LoginRequiredMixin, View):
    """
    Handles the deletion of an API key.
    """

    def post(self, request, *args, **kwargs):
        # get primary key from the URL
        pk = kwargs.get("pk")

        # filter by user to ensure they can only delete their key
        api_key = get_object_or_404(APIKey, pk=pk, user=request.user)

        api_key.delete()

        messages.success(request, f"Successfully deleted API key: '{api_key.name}'")

        return redirect("portal:dashboard")
