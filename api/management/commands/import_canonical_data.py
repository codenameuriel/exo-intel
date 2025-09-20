from django.core.management.base import BaseCommand, CommandError

from api.canonical_data_importer import run_canonical_data_import


class Command(BaseCommand):
    help = "Populate database with canonical data, consolidated from the NASA TAP API"

    def handle(self, *args, **kwargs):
        try:
            run_canonical_data_import(logger=self._command_logger)
        except Exception as e:
            raise CommandError("An error occurred") from e

    # TODO: refactor this into a logger class
    def _command_logger(self, message):
        if "ERROR" in message or "FATAL" in message:
            self.stdout.write(self.style.ERROR(message))
        elif "WARNING" in message:
            self.stdout.write(self.style.WARNING(message))
        else:
            self.stdout.write(self.style.SUCCESS(message))
