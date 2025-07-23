import math
from planets.models import Planet, StarSystem


class SimulationError(Exception):
    pass


class SimulationEngine:
    """
    A class to house various scientific simulation and calculation methods.
    """

    # 1 parsec to light year
    PARSEC_TO_LIGHT_YEAR = 3.26156
    # total energy radiated to absolute temperature
    STEFAN_BOLTZMANN_CONSTANT = 5.670374e-8  # W⋅m−2⋅K−4
    # total energy radiated of the Sun
    SOLAR_LUMINOSITY = 3.828e26  # Watts
    # astronomical Unit (average distance from Earth to the Sun) in meters
    AU_TO_METERS = 1.496e11
    # radius of the sun in meters
    SOLAR_RADIUS_METERS = 6.957e8
    # Years in a Giga-year
    YEARS_PER_GYR = 1e9
    # sun mass in kg
    SOLAR_MASS_KG = 1.989e30
    # earth mass in kg
    EARTH_MASS_KG = 5.972e24
    # earth radius in meters
    EARTH_RADIUS_METERS = 6.371e6

    @staticmethod
    def calculate_travel_time(star_system_id, speed_percentage):
        """
        Calculates the time it would take to travel to a given star system
        at a certain percentage of the speed of light.
        """
        try:
            star_system = StarSystem.objects.get(pk=star_system_id)
        except StarSystem.DoesNotExist:
            raise SimulationError(f"StarSystem with ID {star_system_id} not found.")

        if star_system.distance is None:
            raise SimulationError(
                "Cannot calculate travel time: Star system is missing distance data."
            )

        distance_in_light_years = (
            star_system.distance * SimulationEngine.PARSEC_TO_LIGHT_YEAR
        )
        # c = speed of light
        speed_as_fraction_of_c = speed_percentage / 100.0
        # time = distance / speed
        travel_time_in_years = distance_in_light_years / speed_as_fraction_of_c

        return {
            "star_system_name": star_system.name,
            "travel_speed_percentage_c": speed_percentage,
            "travel_time_years": round(travel_time_in_years, 2),
        }

    @staticmethod
    def calculate_seasonal_temperatures(planet_id):
        """
        Calculates the equilibrium temperature of a planet at its closest (periastron)
        and farthest (apoastron) points in its orbit.
        """
        try:
            planet = Planet.objects.select_related("host_star").get(pk=planet_id)
        except Planet.DoesNotExist:
            raise SimulationError(f"Planet with ID {planet_id} not found.")

        if planet.semi_major_axis is None or planet.orbital_eccentricity is None:
            raise SimulationError("Planet is missing required orbital data.")

        # get stellar luminosity
        star_luminosity = SimulationEngine._get_star_luminosity_watts(planet.host_star)
        if star_luminosity is None:
            raise SimulationError("Star is missing required physical data.")

        # calculate orbital distances
        periastron_m = (
            planet.semi_major_axis * (1 - planet.orbital_eccentricity)
        ) * SimulationEngine.AU_TO_METERS
        apoastron_m = (
            planet.semi_major_axis * (1 + planet.orbital_eccentricity)
        ) * SimulationEngine.AU_TO_METERS

        # calculate temperatures
        flux_at_periastron = SimulationEngine._calculate_flux(
            star_luminosity, periastron_m
        )
        max_temp = SimulationEngine._convert_flux_to_temp(flux_at_periastron)

        flux_at_apoastron = SimulationEngine._calculate_flux(
            star_luminosity, apoastron_m
        )
        min_temp = SimulationEngine._convert_flux_to_temp(flux_at_apoastron)

        return {
            "planet_name": planet.name,
            "star_name": planet.host_star.name,
            "orbital_eccentricity": planet.orbital_eccentricity,
            "semi_major_axis_au": planet.semi_major_axis,
            "periastron_temp_k": max_temp,
            "apoastron_temp_k": min_temp,
            "seasonal_temp_difference_k": max_temp - min_temp,
        }

    @staticmethod
    def estimate_tidal_locking(planet_id):
        """
        Estimates if a planet is likely to be tidally locked to its star
        using the tidal locking timescale formula.
        """
        try:
            planet = Planet.objects.select_related("host_star").get(pk=planet_id)
        except Planet.DoesNotExist:
            raise SimulationError(f"Planet with ID {planet_id} not found.")

        star = planet.host_star
        required_fields = {
            "planet": [planet.mass_earth, planet.radius_earth, planet.semi_major_axis],
            "star": [star.mass, star.age],
        }

        if any(
            val is None for val in required_fields["planet"] + required_fields["star"]
        ):
            raise SimulationError(
                "Planet or star is missing required data (orbital distance, earth mass, earth radius, star mass, or star age)."
            )

        # simplified version of the tidal locking timescale formula
        orbital_distance_m = planet.semi_major_axis * SimulationEngine.AU_TO_METERS
        planet_mass_kg = planet.mass_earth * SimulationEngine.EARTH_MASS_KG
        star_mass_kg = star.mass * SimulationEngine.SOLAR_MASS_KG
        planet_radius_m = planet.radius_earth * SimulationEngine.EARTH_RADIUS_METERS

        # simplified lumped constant for the formula, assuming Earth-like rigidity
        k_constant = 6e10

        timescale_years = (
            k_constant
            * (orbital_distance_m**6)
            * planet_mass_kg
            / (star_mass_kg**2 * planet_radius_m**3)
        )

        # star's age in given in Giga-years (billions of years)
        star_age_years = star.st_age * SimulationEngine.YEARS_PER_GYR

        is_locked = timescale_years < star_age_years

        if is_locked:
            conclusion = f"The planet is likely tidally locked. The calculated locking time ({timescale_years:,.0f} years) is less than the star's age ({star_age_years:,.0f} years)."
        else:
            conclusion = f"The planet is likely NOT tidally locked. The calculated locking time ({timescale_years:,.0f} years) is greater than the star's age ({star_age_years:,.0f} years)."

        return {
            "planet_name": planet.name,
            "star_name": star.name,
            "is_likely_tidally_locked": is_locked,
            "locking_timescale_years": round(timescale_years),
            "star_age_years": round(star_age_years),
            "conclusion": conclusion,
        }

    @staticmethod
    def _calculate_flux(luminosity_watts, distance_m):
        """
        Calculates the energy flux at a given distance.
        """
        if distance_m <= 0:
            return float("inf")
        return luminosity_watts / (4 * math.pi * (distance_m**2))

    @staticmethod
    def _convert_flux_to_temp(flux, albedo=0.3):
        """
        Converts flux to equilibrium temperature using the Stefan-Boltzmann law.
        """
        if flux == float("inf"):
            return float("inf")
        # T = ( (Flux * (1 - albedo)) / (4 * sigma) ) ^ 0.25
        temperature = (
            (flux * (1 - albedo)) / (4 * SimulationEngine.STEFAN_BOLTZMANN_CONSTANT)
        ) ** 0.25
        return round(temperature)

    @staticmethod
    def _get_star_luminosity_watts(star):
        """
        Determines a star's luminosity in Watts.
        """
        if star.luminosity is not None:
            return (10**star.luminosity) * SimulationEngine.SOLAR_LUMINOSITY
        elif star.radius is not None and star.temperature is not None:
            # fallback: calculate from radius and temperature
            star_radius_m = star.radius * SimulationEngine.SOLAR_RADIUS_METERS
            star_temp_k = star.temperature
            return (
                4
                * math.pi
                * (star_radius_m**2)
                * SimulationEngine.STEFAN_BOLTZMANN_CONSTANT
                * (star_temp_k**4)
            )
        else:
            return None
