"""Automatic assignment of product locations."""
import abc
import datetime
import logging
import typing

import django.utils.timezone
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from ms_baseline.models import Store
from ms_maps.models import ProductLocation, Subaisle
from ms_maps.utils import get_missing_product_locations

py_logger = logging.getLogger("maps_auto_assign")


class AutoAssignLogWriter(abc.ABC):
    """A writer that can produce HTML auto-assignment logs. Also logs to server logs."""

    @abc.abstractmethod
    def log_debug(self, message: str):
        """Log a debug message."""
        ...

    @abc.abstractmethod
    def log_info(self, message: str):
        """Log an info message."""
        ...

    @abc.abstractmethod
    def log_success(self, message: str):
        """Log a success message."""
        ...

    @abc.abstractmethod
    def log_error(self, message: str):
        """Log an error message."""
        ...


class AutoAssignHtmlLogWriter(AutoAssignLogWriter):
    """A writer that can produce HTML auto-assignment logs. Also logs to server logs."""

    HTML_FORMAT: str = '<div class="{0}">{1}</div>'
    lines: typing.List[SafeString]

    def __init__(self):
        """Initialize the log writer."""
        self.lines = []

    def log_debug(self, message: str):
        """Log a debug message."""
        py_logger.debug(message)
        self.lines.append(format_html(self.HTML_FORMAT, "text-muted", message))

    def log_info(self, message: str):
        """Log an info message."""
        py_logger.info(message)
        self.lines.append(format_html(self.HTML_FORMAT, "", message))

    def log_success(self, message: str):
        """Log a success message."""
        py_logger.info(message)
        self.lines.append(format_html(self.HTML_FORMAT, "text-success", message))

    def log_error(self, message: str):
        """Log an error message."""
        py_logger.error(message)
        self.lines.append(format_html(self.HTML_FORMAT, "text-danger", message))

    def get(self) -> SafeString:
        """Get the log in HTML format."""
        return mark_safe("\n".join(self.lines))


def auto_assign(
    log: AutoAssignLogWriter,
    stores: typing.Optional[typing.Iterable[Store]] = None,
    now: typing.Optional[datetime.datetime] = None,
):
    """Automatically assign product locations in all stores."""
    if not now:
        now = django.utils.timezone.now()
    if not stores:
        stores = Store.objects.filter(hidden=False)
    log.log_info(_("Starting assigning automated locations."))
    new_assignments = 0
    for store in stores:
        log.log_info(_("Assigning locations in {store}").format(store=store))
        new_assignments += auto_assign_in_store(store, log, now)
    log.log_success(
        ngettext(
            "Automated assignments complete. Assigned {} location.",
            "Automated assignments complete. Assigned {} locations.",
            new_assignments,
        ).format(new_assignments)
    )
    return new_assignments


def auto_assign_in_store(store: Store, log: AutoAssignLogWriter, now: typing.Optional[datetime.datetime] = None):
    """Automatically assign product locations in a store."""
    if not now:
        now = django.utils.timezone.now()
    missing = get_missing_product_locations(store, now)
    new_assignments = 0
    for product in missing:
        loc = ProductLocation.create_auto_location(product, store, now)
        if loc:
            log.log_success(_("==> Assigned {loc.subaisle} to {loc.product}").format(loc=loc))
            new_assignments += 1
        else:
            count = Subaisle.objects.filter(store=store, subcategories=product.subcategory).count()
            if count == 0:
                log.log_debug(
                    _("==> Unable to assign location to {product}: no aisle for {product.subcategory}").format(
                        product=product
                    )
                )
            elif count == 1:
                log.log_error(
                    _("==> Failed to assign location to {product}, but candidate subaisle exists.").format(
                        product=product
                    )
                )
            else:
                log.log_error(
                    _("==> Unable to assign location to {product}: multiple aisles for {product.subcategory}").format(
                        product=product
                    )
                )
    return new_assignments
