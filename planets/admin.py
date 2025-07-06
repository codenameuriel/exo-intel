from django.contrib import admin

# Register your models here.
from .models import StarSystem, Star, PlanetDiscovery, Planet

class ReadOnlyAdmin(admin.ModelAdmin):
    """
    Admin class that makes a model read-only.
    """
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(StarSystem)
class StarSystemAdmin(ReadOnlyAdmin):
    list_display = ('name', 'num_stars', 'num_planets', 'num_moons', 'distance', 'ra', 'dec')
    ordering = ('name',)
    search_fields = ('name',)
    list_filter = ('name', 'num_stars', 'num_planets', 'num_moons', 'ra', 'dec')

@admin.register(Star)
class StarAdmin(ReadOnlyAdmin):
    list_display = ('name', 'system', 'spect_type', 'mass', 'radius', 'temperature')
    ordering = ('name',)
    search_fields = ('name', 'system__name')
    list_filter = ('system', 'spect_type')

@admin.register(PlanetDiscovery)
class PlanetDiscoveryAdmin(ReadOnlyAdmin):
    list_display = ('method', 'year', 'locale', 'facility')
    ordering = ('year',)
    search_fields = ('method', 'year', 'locale', 'facility')
    list_filter = ('method', 'year', 'locale', 'facility')

@admin.register(Planet)
class PlanetAdmin(ReadOnlyAdmin):
    list_display = ('name', 'host_star', 'orbital_period', 'radius_earth', 'mass_earth', 'equilibrium_temperature', 'semi_major_axis', 'insolation_flux')
    ordering = ('name',)
    search_fields = ('name', 'host_star__name')
    list_filter = ('host_star__system', 'discovery__method', 'discovery__facility')