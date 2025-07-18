import time
from celery import shared_task, chain
from planets.importer import run_import
from planets.models import StarSystem
from planets.simulations import SimulationEngine


@shared_task
def full_nightly_import():
    """
    A master task that runs the full import pipeline in the correct order
    """
    import_chain = chain(
        import_nasa_data_task.si("stellarhosts", "starsystem"),
        import_nasa_data_task.si("stellarhosts", "star"),
        import_nasa_data_task.si("ps", "planetdiscovery"),
        import_nasa_data_task.si("ps", "planet"),
    )

    import_chain()


@shared_task
def import_nasa_data_task(nasa_table, app_table):
    """
    A Celery task to fetch data from NASA TAP API and populate the database
    """

    print(f"Starting background import for '{app_table}'...")

    result = run_import(nasa_table=nasa_table, app_table=app_table, logger=print)

    print(f"Final result: {result}")

    return result


@shared_task
def travel_time_simulation_task(star_system_id, speed_percentage):
    """
    A Celery task to run the travel time simulation in the background
    """
    print(f"Starting travel time simulation for start system ID: {star_system_id}...")

    try:
        star_system = StarSystem.objects.get(pk=star_system_id)

        print(f"Simulation in progress...")
        time.sleep(10)

        travel_time = SimulationEngine.calculate_travel_time(
            star_system, speed_percentage
        )

        if travel_time is None:
            result = {
                "error": "Could not calculate travel time. Missing distance data."
            }
        else:
            result = {
                "star_system_name": star_system.name,
                "travel_speed_percentage_c": speed_percentage,
                "travel_time_years": travel_time,
            }

        print("Simulation complete.")
        return result

    except StarSystem.DoesNotExist:
        print(f"ERROR: StarSystem with ID {star_system_id} not found.")
        return {"error": f"StarSystem with ID {star_system_id} not found."}
    except ValueError as e:
        print(f"ERROR: Invalid input for simulation. {e}")
        return {"error": str(e)}
