from django.db import models

# Create your models here.
class Star(models.Model):
    name = models.CharField(max_length=100, unique=True)
    mass = models.FloatField(null=True, help_text="Mass in solar masses")
    radius = models.FloatField(null=True, help_text="Radius in solar radii")
    temperature = models.FloatField(null=True, help_text="Effective temperature (K)")
    distance = models.FloatField(null=True, help_text="Distance from Earth in parsecs")
    ra = models.FloatField(null=True, help_text="Right Ascension")
    dec = models.FloatField(null=True, help_text="Declination")

    def __str__(self):
        return self.name

class Planet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    host_star = models.ForeignKey(Star, on_delete=models.CASCADE, related_name='planets')
    orbital_period = models.FloatField(null=True, help_text="Orbital period in days")
    radius = models.FloatField(null=True, help_text="Radius in Earth radii")
    mass = models.FloatField(null=True, help_text="Mass in Earth masses")
    equilibrium_temperature = models.IntegerField(null=True, help_text="Temperature in Kelvin")
    semi_major_axis = models.FloatField(null=True, help_text="Distance from star in AU")
    discovery_method = models.CharField(max_length=100, null=True, blank=True)
    discovered_year = models.IntegerField(null=True)
    insolation_flux = models.FloatField(null=True, help_text="Flux relative to Earth = 1.0")

    def __str__(self):
        return self.name