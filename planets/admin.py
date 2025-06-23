from django.contrib import admin

# Register your models here.
from .models import StarSystem, Star, PlanetDiscovery, Planet

@admin.register(StarSystem)
class StarSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'num_stars', 'num_planets', 'num_moons', 'distance', 'ra', 'dec')
    search_fields = ('name',)

@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = ('name', 'system', 'spect_type', 'mass', 'radius', 'temperature')
    search_fields = ()

@admin.register(PlanetDiscovery)
class PlanetDiscoveryAdmin(admin.ModelAdmin):
    list_display = ('method', 'year', 'locale', 'facility')
    search_fields = ()

@admin.register(Planet)
class PlanetAdmin(admin.ModelAdmin):
    list_display = ('name', 'host_star', 'orbital_period', 'radius_earth', 'mass_earth', 'equilibrium_temperature', 'semi_major_axis', 'insolation_flux')
    search_fields = ()