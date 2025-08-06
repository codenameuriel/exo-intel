from django.core.management.base import BaseCommand, CommandError
from planets.importer import run_import


NASA_TABLES = ["stellarhosts", "ps"]
APP_TABLES = ["star_systems", "stars", "planet_discoveries", "planets"]


class Command(BaseCommand):
    help = "Fetch data from NASA TAP service and populate database"


    def add_arguments(self, parser):
        parser.add_argument(
            "--nasa-table",
            type=str,
            choices=NASA_TABLES,
            required=True,
            help="Which NASA table to import from",
        )

        parser.add_argument(
            "--app-table",
            type=str,
            choices=APP_TABLES,
            required=True,
            help="Which app table to import into",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print actions without modifying the database",
        )


    def handle(self, *args, **kwargs):
        nasa_table = kwargs["nasa_table"]
        app_table = kwargs["app_table"]
        dry_run = kwargs["dry_run"]

        try:
            result = run_import(
                nasa_table=nasa_table,
                app_table=app_table,
                dry_run=dry_run,
                logger=self._command_logger,
            )

            self.stdout.write(self.style.SUCCESS(f"Final result: {result}"))
        except Exception as e:
            raise CommandError(f"An unexpected error occurred: {e}")


    def _command_logger(self, message):
        if "ERROR" in message or "FATAL" in message:
            self.stdout.write(self.style.ERROR(message))
        elif "WARNING" in message:
            self.stdout.write(self.style.WARNING(message))
        else:
            self.stdout.write(self.style.SUCCESS(message))