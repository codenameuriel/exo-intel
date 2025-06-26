from django.db import models

class StarSystem(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the system")
    num_stars = models.IntegerField(null=True, blank=True, help_text="Number of stars")
    num_planets = models.IntegerField(null=True, blank=True, help_text="Number of planets")
    num_moons = models.IntegerField(null=True, blank=True, help_text="Number of moons")
    distance = models.FloatField(null=True, blank=True, help_text="Distance from Earth in parsecs")
    ra = models.FloatField(null=True, blank=True, help_text="Right Ascension")
    dec = models.FloatField(null=True, blank=True, help_text="Declination")

    class Meta:
        verbose_name = "Star System"
        verbose_name_plural = "Star Systems"

    def __str__(self):
        return self.name

class Star(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the star")
    system = models.ForeignKey(StarSystem, on_delete=models.CASCADE, help_text="The system")
    spect_type = models.CharField(max_length=30, null=True, blank=True, help_text="Spectral type")
    mass = models.FloatField(null=True, blank=True, help_text="Mass in solar masses")
    radius = models.FloatField(null=True, blank=True, help_text="Radius in solar radii")
    temperature = models.FloatField(null=True, blank=True, help_text="Effective temperature (K)")

    def __str__(self):
        return self.name

class PlanetDiscovery(models.Model):
    method = models.CharField(max_length=100, help_text="Discovery method")
    year = models.IntegerField(null=True, blank=True, help_text="Year of discovery")
    locale = models.CharField(max_length=50, help_text="Location of observation (Ground or Space)")
    facility = models.CharField(max_length=100, help_text="Name of facility")

    class Meta:
        verbose_name = "Planet Discovery"
        verbose_name_plural = "Planet Discoveries"

    def __str__(self):
        return f"{self.method} @ {self.facility} ({self.facility})"

class Planet(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Name of the planet")
    host_star = models.ForeignKey(Star, on_delete=models.CASCADE, help_text="The host star")
    orbital_period = models.FloatField(null=True, blank=True, help_text="Orbital period in days")
    radius_earth = models.FloatField(null=True, blank=True, help_text="Radius in Earth radii")
    mass_earth = models.FloatField(null=True, blank=True, help_text="Mass in Earth masses")
    equilibrium_temperature = models.FloatField(null=True, blank=True, help_text="Temperature in Kelvin")
    semi_major_axis = models.FloatField(null=True, blank=True, help_text="Distance from star in AU")
    insolation_flux = models.FloatField(null=True, blank=True, help_text="Flux relative to Earth = 1.0")
    discovery = models.ForeignKey(PlanetDiscovery, on_delete=models.CASCADE, help_text="Planet discovery", null=True, blank=True)

    def __str__(self):
        return f"{self.name} (orbits {self.host_star.name})"