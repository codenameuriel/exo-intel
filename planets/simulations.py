class SimulationEngine:
    """
    A class to house various scientific simulation and calculation methods.
    """

    PARSEC_TO_LIGHT_YEAR = 3.26156

    @staticmethod
    def calculate_travel_time(star_system, speed_percentage):
        """
        Calculates the time it would take to travel to a given star system
        at a certain percentage of the speed of light.

        :param star_system: The destination StarSystem object.
        :param speed_percentage: The travel speed as a percentage of the speed of light (1-100).
        :return: The calculated travel time in years, or None if calculation is not possible.
        """
        if not star_system or star_system.distance is None:
            return None

        if not (0 < speed_percentage <= 100):
            raise ValueError("Speed percentage must be between 1 and 100")

        distance_in_light_years = (
            star_system.distance * SimulationEngine.PARSEC_TO_LIGHT_YEAR
        )
        # c = speed of light
        speed_as_fraction_of_c = speed_percentage / 100.0
        # time = distance / speed
        travel_time_in_years = distance_in_light_years / speed_as_fraction_of_c

        return round(travel_time_in_years, 2)
