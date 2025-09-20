from django.core.management.base import BaseCommand, CommandError

from scripts.canonical_data_consolidater import run_canonical_data_consolidation


class Command(BaseCommand):
    help = "Fetch data from NASA TAP service, consolidate data into canonical records, and save to JSON files"

    def handle(self, *args, **kwargs):
        try:
            result = run_canonical_data_consolidation(logger=self._command_logger)
            self._command_logger(result)
        except Exception as e:
            raise CommandError("An error occurred") from e

    def _command_logger(self, message):
        if "ERROR" in message or "FATAL" in message:
            self.stdout.write(self.style.ERROR(message))
        elif "WARNING" in message:
            self.stdout.write(self.style.WARNING(message))
        else:
            self.stdout.write(self.style.SUCCESS(message))
