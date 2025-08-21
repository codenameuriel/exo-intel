import time

from celery import chain, shared_task
from django.contrib.auth.models import User
from django.db.models.functions import Now

from api.importer import run_import
from simulations.engine import SimulationEngine, SimulationError
from simulations.models import SimulationRun

from .exceptions import TaskError

SIMULATION_DISPATCHER = {
    SimulationRun.SimulationType.TRAVEL_TIME: SimulationEngine.calculate_travel_time,
    SimulationRun.SimulationType.SEASONAL_TEMPS: SimulationEngine.calculate_seasonal_temperatures,
    SimulationRun.SimulationType.TIDAL_LOCKING: SimulationEngine.estimate_tidal_locking,
    SimulationRun.SimulationType.STAR_LIFETIME: SimulationEngine.calculate_star_lifetime,
}


@shared_task
def full_nightly_import():
    """
    A master task that runs the full import pipeline in the correct order
    """
    import_chain = chain(
        import_nasa_data_task.si("stellarhosts", "star_systems"),
        import_nasa_data_task.si("stellarhosts", "stars"),
        import_nasa_data_task.si("ps", "planet_discoveries"),
        import_nasa_data_task.si("ps", "planets"),
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


@shared_task(bind=True)
def run_simulation_task(self, user_id, simulation_type, input_parameters):
    """
    A generic Celery task that dispatches simulation runs.
    """
    try:
        user = User.objects.get(pk=user_id)
        run = SimulationRun.objects.create(
            user=user,
            task_id=self.request.id,
            simulation_type=simulation_type,
            input_parameters=input_parameters,
            status=SimulationRun.Status.PENDING,
        )
    except User.DoesNotExist:
        print(f"[TASKERR]: User with ID '{user_id}' not found.", flush=True)
        raise TaskError(f"User with ID '{user_id}' not found.")
    except Exception as e:
        print(
            f"[TASKERR]: Could not create SimulationRun history record: {e}", flush=True
        )
        raise TaskError(f"Failed to initialize history record: {e}")

    try:
        simulation_func = SIMULATION_DISPATCHER[simulation_type]
    except KeyError:
        print(f"[TASKERR]: Unknown simulation type '{simulation_type}'", flush=True)
        SimulationRun.objects.filter(pk=run.pk).update(
            status=SimulationRun.Status.FAILURE,
            result={"error": "Unknown simulation type"},
            completed_at=Now(),
        )
        raise TaskError(f"Unknown simulation type '{simulation_type}'")

    try:
        print(
            f"Dispatching simulation '{simulation_type}' with inputs: {input_parameters}",
            flush=True,
        )
        time.sleep(10)  # simulate long-running process

        result = simulation_func(**input_parameters)

        run.status = SimulationRun.Status.SUCCESS
        run.result = result

        print("Simulation complete.", flush=True)

        return result
    except (SimulationError, TaskError) as e:
        run.status = SimulationRun.Status.FAILURE
        run.result = {"error": str(e)}
        raise e
    finally:
        SimulationRun.objects.filter(pk=run.pk).update(
            status=run.status, result=run.result, completed_at=Now()
        )
