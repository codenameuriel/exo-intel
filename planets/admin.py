from django.contrib import admin

# Register your models here.
from .models import Star, Planet

@admin.register(Star)
class StarAdmin(admin.ModelAdmin):
    list_display = ('name', 'mass', 'radius', 'temperature', 'distance')
    search_fields = ()

@admin.register(Planet)
class PlanetAdmin(admin.ModelAdmin):
    list_display = ('name', 'host_star', 'orbital_period', 'radius', 'mass', 'discovered_year')
    search_fields = ()