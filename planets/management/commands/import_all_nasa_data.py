from django.core.management.base import BaseCommand, CommandError

from planets.importer import run_import


class Command(BaseCommand):
    help = "Populate database with data from NASA TAP API"

    def handle(self, *args, **kwargs):
        self._command_logger("--- Starting Full Database Import ---\n")

        TABLE_MAPPINGS = [
            ("stellarhosts", "star_systems"),
            ("stellarhosts", "stars"),
            ("ps", "planet_discoveries"),
            ("ps", "planets"),
        ]

        for nasa_table, app_table in TABLE_MAPPINGS:
            try:
                run_import(
                    nasa_table=nasa_table,
                    app_table=app_table,
                    logger=self._command_logger,
                )

                self._command_logger(f"Successfully populated {app_table} table.\n")
            except Exception as e:
                raise CommandError(f"Failed to populate {app_table} table. ERROR: {e}")

        self._command_logger("--- Finished Full Database Import ---")

    def _command_logger(self, message):
        if "ERROR" in message or "FATAL" in message:
            self.stdout.write(self.style.ERROR(message))
        elif "WARNING" in message:
            self.stdout.write(self.style.WARNING(message))
        else:
            self.stdout.write(self.style.SUCCESS(message))
