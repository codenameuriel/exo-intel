import time
from celery import shared_task, chain
from django.db.models.functions import Now
from django.contrib.auth.models import User

from planets.importer import run_import
from simulations.models import SimulationRun
from simulations.engine import SimulationEngine, SimulationError
from .exceptions import TaskError


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
        print("Simulation in progress...")
        time.sleep(10)

        result = SimulationEngine.calculate_travel_time(
            star_system_id, speed_percentage
        )

        print("Simulation complete.")
        return result
    except SimulationError as e:
        print(f"ERROR: Simulation failed with a known error: {e}")
        # raise the error to mark task as FAILURE
        raise e


@shared_task
def seasonal_temps_simulation_task(planet_id):
    """
    A Celery task to run the seasonal temperatures simulation in the background
    """
    print(f"Starting seasonal temperatures simulation for planet ID: {planet_id}...")

    try:
        print("Simulation in progress...")
        time.sleep(10)

        result = SimulationEngine.calculate_seasonal_temperatures(planet_id)

        print("Simulation complete.")
        return result
    except SimulationError as e:
        print(f"ERROR: Simulation failed with a known error: {e}")
        raise e


@shared_task
def tidal_locking_simulation_task(planet_id):
    """
    A Celery task to run the tidal locking simulation in the background
    """
    print(f"Starting tidal locking simulation for planet ID: {planet_id}...")

    try:
        print("Simulation in progress...")
        time.sleep(10)

        result = SimulationEngine.estimate_tidal_locking(planet_id)

        print("Simulation complete.")
        return result
    except SimulationError as e:
        print(f"ERROR: Simulation failed with a known error: {e}")
        raise e


@shared_task(bind=True)
def star_lifetime_simulation_task(self, user_id, star_id):
    """
    A Celery task to run the star lifetime simulation in the background
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        print(
            f"[TASKERR]: Could not start simulation. User with ID '{user_id}' not found."
        )
        raise TaskError(f"User with ID '{user_id}' not found.")

    try:
        run = SimulationRun.objects.create(
            user=user,
            task_id=self.request.id,
            status=SimulationRun.Status.PENDING,
            simulation_type=SimulationRun.SimulationType.STELLAR_LIFETIME,
            input_parameters={"star_id": star_id},
        )
    except Exception as e:
        print(f"[TASKERR]: Could not create SimulationRun history record: {e}")
        raise TaskError(f"Failed to initialize history record: {e}")

    try:
        print(f"Starting star lifetime simulation for star ID: {star_id}...")
        print("Simulation in progress...")
        time.sleep(10)

        result = SimulationEngine.calculate_star_lifetime(star_id)

        run.status = SimulationRun.Status.SUCCESS
        run.result = result
        print("Simulation complete.")

        return result
    except SimulationError as e:
        print(f"[SIMULATIONERR]: Simulation failed: {e}")
        run.status = SimulationRun.Status.FAILURE
        run.result = {"error": str(e)}
        raise e
    finally:
        SimulationRun.objects.filter(pk=run.pk).update(
            status=run.status,
            result=run.result,
            completed_at=Now(),
        )
