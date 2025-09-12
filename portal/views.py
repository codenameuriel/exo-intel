from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import CreateView
from rest_framework.reverse import reverse_lazy

from api.models import Planet, Star, StarSystem
from api_keys.models import APIKey
from portal.forms import SignupForm


class SignUpView(CreateView):
    """Handles user registration."""

    form_class = SignupForm
    template_name = "portal/signup.html"
    success_url = reverse_lazy("portal:dashboard")

    def form_valid(self, form):
        """Handles valid form data on POST requests."""

        # response is a HttpResponseRedirect
        response = super().form_valid(form)
        # self.object is the created user set by the parent CreateView form_valid method
        login(self.request, self.object)
        return response


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
        travel_sim_star_systems = StarSystem.objects.filter(
            distance_parsecs__isnull=False
        ).order_by("name")

        seasonality_sim_planets = (
            Planet.objects.filter(
                Q(host_star__luminosity_sun__isnull=False)
                | (
                        Q(host_star__radius_sun__isnull=False)
                        & Q(host_star__effective_temperature_k__isnull=False)
                ),
                semi_major_axis_au__isnull=False,
                orbital_eccentricity__isnull=False,
            )
            .select_related("host_star")
            .order_by("name")
            .distinct()
        )

        tidal_locking_sim_planets = (
            Planet.objects.filter(
                Q(host_star__mass_sun__isnull=False) & Q(host_star__age_gya__isnull=False),
                mass_earth__isnull=False,
                radius_earth__isnull=False,
                semi_major_axis_au__isnull=False,
            )
            .select_related("host_star")
            .order_by("name")
            .distinct()
        )

        star_lifetime_sim_stars = Star.objects.filter(
            mass_sun__isnull=False,
            age_gya__isnull=False,
        ).order_by("name")

        context = {
            "api_keys": api_keys,
            "api_key_count": api_keys.count(),
            "travel_sim_star_systems": travel_sim_star_systems,
            "seasonality_sim_planets": seasonality_sim_planets,
            "tidal_locking_sim_planets": tidal_locking_sim_planets,
            "star_lifetime_sim_stars": star_lifetime_sim_stars,
        }

        return render(request, self.template_name, context)


class APIKeyCreateView(LoginRequiredMixin, View):
    """
    Handle POST requests from the api key generation form.
    Creates a new API key for the logged-in user.
    """

    def post(self, request, *args, **kwargs):
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
