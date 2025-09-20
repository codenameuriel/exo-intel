import time

from celery import chain, shared_task
from celery.utils.log import get_task_logger
from django.contrib.auth.models import User
from django.db import Error as DatabaseError
from django.db.models.functions import Now

from api.canonical_data_importer import run_canonical_data_import
from api.importer import run_import
from scripts.canonical_data_consolidater import run_canonical_data_consolidation
from simulations.engine import SimulationEngine, SimulationError
from simulations.models import SimulationRun
from .exceptions import TaskError

# use Celery logger for additional logging context
logger = get_task_logger(__name__)

SIMULATION_DISPATCHER = {
    SimulationRun.SimulationType.TRAVEL_TIME: SimulationEngine.calculate_travel_time,
    SimulationRun.SimulationType.SEASONAL_TEMPS: SimulationEngine.calculate_seasonal_temperatures,
    SimulationRun.SimulationType.TIDAL_LOCKING: SimulationEngine.estimate_tidal_locking,
    SimulationRun.SimulationType.STAR_LIFETIME: SimulationEngine.calculate_star_lifetime,
}


@shared_task
def canonical_data_consolidation():
    """
    A task to consolidate the NASA TAP API data into canonical data JSON files
    """
    try:
        logger.info("--- Starting Canonical Data Consolidation ---")
        result_message = run_canonical_data_consolidation(logger=logger.info)
        logger.info(f"--- Finished Canonical Data Consolidation: {result_message} ---")
        return result_message
    except Exception as e:
        message = "An unexpected error occurred during the canonical data consolidation."
        logger.error(message, exc_info=True)
        raise TaskError(message) from e


@shared_task
def canonical_data_import():
    """
    A task to import the canonical data JSON files into the database
    """
    try:
        logger.info("--- Starting Canonical Data Import ---")
        result_message = run_canonical_data_import(dry_run=False, logger=logger.info)
        logger.info(f"--- Finished Canonical Data Import: {result_message} ---")
        # used by Celery Results backend
        return result_message
    except Exception as e:
        message = "An unexpected error occurred during the canonical data import."
        logger.error(message, exc_info=True)
        raise TaskError(message) from e


@shared_task
def full_nightly_canonical_import(dry_run=False):
    """
    A master task that runs the full canonical data creation and import pipeline
    """
    canonical_data_import_chain = chain(
        canonical_data_consolidation.si(),
        canonical_data_import.si(),
    )

    canonical_data_import_chain()


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
    logger.info(f"Starting background import for '{app_table}'...")

    result = run_import(nasa_table=nasa_table, app_table=app_table, logger=logger.info)

    logger.info(f"Final result: {result}")

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
    except User.DoesNotExist as e:
        message = f"User with ID '{user_id}' not found."
        logger.error(message, exc_info=True)
        raise TaskError(message) from e
    except DatabaseError as e:
        message = "A database error occurred while creating SimulationRun history record"
        logger.error(message, exc_info=True)
        raise TaskError(message) from e
    except Exception as e:
        message = "An unexpected error occurred while creating SimulationRun history record"
        logger.error(message, exc_info=True)
        raise TaskError(message) from e

    try:
        simulation_func = SIMULATION_DISPATCHER[simulation_type]
    except KeyError as e:
        message = f"Unknown simulation type '{simulation_type}'"
        logger.error(message, exc_info=True)

        SimulationRun.objects.filter(pk=run.pk).update(
            status=SimulationRun.Status.FAILURE,
            result={"error": "Unknown simulation type"},
            completed_at=Now(),
        )

        raise TaskError(message) from e

    try:
        logger.info(
            f"Dispatching simulation '{simulation_type}' with inputs: {input_parameters}",
        )

        time.sleep(5)  # simulate a long-running process

        result = simulation_func(**input_parameters)

        run.status = SimulationRun.Status.SUCCESS
        run.result = result

        logger.info("Simulation complete.")

        return result
    except SimulationError as e:
        message = str(e)
        logger.error(message, exc_info=True)
        run.status = SimulationRun.Status.FAILURE
        run.result = {"error": message}
        raise TaskError(message) from e
    finally:
        SimulationRun.objects.filter(pk=run.pk).update(
            status=run.status, result=run.result, completed_at=Now()
        )
