"""Automatically assign product locations in stores."""
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _

from ms_baseline.models import Store
from ms_maps.auto_assign import AutoAssignLogWriter, auto_assign


class Command(BaseCommand, AutoAssignLogWriter):
    """Automatically assign product locations in stores."""

    help = "Automatically assigns product locations in stores"

    def add_arguments(self, parser):
        """Add an argument to select stores to assign locations in."""
        parser.add_argument("store_ids", nargs="*", type=int, help="Store IDs to assign in (default: all non-hidden)")

    def handle(self, *args, **options):
        """Run the auto assignment command."""
        stores = []
        for id in options["store_ids"]:
            try:
                stores.append(Store.objects.get(pk=id))
            except Store.DoesNotExist:
                raise CommandError(_("Store {} does not exist!".format(id)))

        auto_assign(self, stores)

    def log_debug(self, message):
        """Log a debug message."""
        self.stdout.write(message)

    def log_info(self, message):
        """Log an info message."""
        self.stdout.write(self.style.HTTP_INFO(message))

    def log_success(self, message):
        """Log a success message."""
        self.stdout.write(self.style.SUCCESS(message))

    def log_error(self, message):
        """Log an error message."""
        self.stderr.write(self.style.ERROR(message))
