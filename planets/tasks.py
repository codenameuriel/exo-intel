from celery import shared_task, chain
from planets.importer import run_import


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
