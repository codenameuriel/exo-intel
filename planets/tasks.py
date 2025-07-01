from celery import shared_task
from planets.importer import run_import

@shared_task
def import_nasa_data(nasa_table, app_table):
    """
    A Celery task to fetch data from NASA and populate the database
    """

    print(f"Starting background import for '{app_table}'...")

    try:
        result = run_import(
        nasa_table=nasa_table,
        app_table=app_table,
        logger=print)
        print(f"Final result: {result}")
    except Exception as e:
        raise (f"An unexpected error occurred: {e}")
