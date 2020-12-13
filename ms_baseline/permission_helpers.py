"""Definitions of decorators that check permissions."""
import functools
import logging

from django.utils.translation import gettext as _

from ms_baseline.utils import _render_no_access, render

logger = logging.getLogger("ms_baseline.permissions")


class PermissionDenied(BaseException):
    """An exception raised when permissions are denied."""

    def __init__(self, msg=None):
        """Initialize the exception."""
        if not msg:
            msg = _("Permission denied")
        super().__init__(self, msg)


def permissions_required(loc=None, glob=None, groups=None):
    """Make a page require permissions."""

    def pr_wrapper(view):
        """Wrap a function with the permissions checker."""

        @functools.wraps(view)
        def pr_checker(request, *args, **kwargs):
            """Check permissions for a view."""
            can_access = False
            if not request.user.is_authenticated or not (
                request.user.is_manager or request.user.is_global_manager or request.user.is_superuser
            ):
                logger.debug(f"Denied access to {view} to non-manager user {request.user.pk} ({request.user})")
                return render(request, "mobishopper/deny_unauthorized.html", _("Forbidden"), {}, status=403)
            if groups:
                can_access = any(getattr(request.user, p) for p in groups)
            elif request.ms_store is None:
                if not request.user.is_global_manager and not request.user.is_superuser:
                    return _render_no_access(request)
                can_access = any(getattr(request.user, p) for p in glob)
                if glob is None:
                    can_access = True
            else:
                if not request.user.is_manager:
                    return _render_no_access(request)
                if loc is None:
                    can_access = True
                else:
                    can_access = any(getattr(request.ms_store_permission, p) for p in loc)
            if can_access:
                try:
                    return view(request, *args, **kwargs)
                except PermissionDenied:
                    logger.warning(f"View {view} denied access to user {request.user.pk} ({request.user})")
                    return _render_no_access(request)
            else:
                logger.warning(f"Permissions denied access to view {view} to user {request.user.pk} ({request.user})")
                return _render_no_access(request)

        return pr_checker

    return pr_wrapper


permissions_required_users = permissions_required(
    loc=["can_manage_employees"], glob=["can_manage_users", "is_superuser"]
)

permissions_required_stores = permissions_required(glob=["can_manage_stores", "is_superuser"])

permissions_required_products_readonly = permissions_required(groups=["is_management_employee"])

permissions_required_products = permissions_required(loc=["can_manage_products"], glob=["can_manage_global_products"])

permissions_required_products_local = permissions_required(loc=["can_manage_products"], glob=[])
permissions_required_products_global = permissions_required(loc=[], glob=["can_manage_global_products"])

permissions_required_deals = permissions_required(loc=["can_manage_deals"], glob=["can_manage_global_deals"])
permissions_required_deals_local = permissions_required(loc=["can_manage_deals"], glob=[])
permissions_required_deals_global = permissions_required(loc=[], glob=["can_manage_global_deals"])

permissions_required_maps = permissions_required(loc=["can_manage_maps"], glob=[])

permissions_required_stats = permissions_required(loc=["can_view_statistics"], glob=["can_view_global_statistics"])


def editable_in_store_context(request, obj):
    """Check if an object is editable in the current store context."""
    return request.ms_store is None or obj.store == request.ms_store


def permissions_required_custom(checker):
    """Make a page require permissions with a custom checker function."""

    def prc_wrapper(view):
        """Wrap a function with the permissions checker."""

        @functools.wraps(view)
        def prc_checker(request, *args, **kwargs):
            """Check permissions for a view."""
            if not request.user.is_authenticated or not (
                request.user.is_manager or request.user.is_global_manager or request.user.is_superuser
            ):
                return render(request, "mobishopper/deny_unauthorized.html", _("Forbidden"), {}, status=403)
            if checker(request.user, request.ms_store_permission):
                try:
                    return view(request, *args, **kwargs)
                except PermissionDenied:
                    return _render_no_access(request)
            else:
                return _render_no_access(request)

        return prc_checker

    return prc_wrapper
