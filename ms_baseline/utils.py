"""Utils for ms_baseline."""
import decimal
import functools
import typing
import urllib.parse

import django.core.paginator
import django.shortcuts
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import gettext as _

from . import constants
from .models import Store, UserStorePermission


class StoreContextMiddleware:
    """Middleware to add store context."""

    def __init__(self, get_response):
        """Initialize middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Handle a request."""
        store_context = get_store_context(request)
        request.ms_permissions = store_context["ms_permissions"]
        request.ms_store = store_context["ms_store"]
        request.ms_store_permission = store_context["ms_store_permission"]
        request.visited_store = store_context["visited_store"]
        request.resolved_store = store_context["resolved_store"]
        response = self.get_response(request)
        return response


def get_store_context(request) -> dict:
    """Get the store context."""
    context = {
        "visited_store": None,
        "resolved_store": None,
        "ms_store": None,
        "ms_store_permission": None,
        "ms_permissions": [],
    }
    visited_store_id = request.headers.get("X-MS-Store")  # Mobile app sends this header
    if visited_store_id:
        context["visited_store"] = Store.objects.get(id=visited_store_id)
    elif request.user.is_authenticated and not request.user.is_employee and request.user.default_store_id:
        try:
            context["visited_store"] = Store.objects.get(id=request.user.default_store_id)
        except Store.DoesNotExist:
            pass
    context["resolved_store"] = context["visited_store"]

    if not request.user.is_authenticated or not request.user.is_employee:
        return context

    context["ms_permissions"] = UserStorePermission.objects.filter(user=request.user)
    if not context["ms_permissions"]:
        return context
    has_session = hasattr(request, "session")
    if has_session and "store" in request.session:
        if request.session["store"] == "":
            # Global mode
            context["ms_store"] = None
            context["ms_store_permission"] = None
            context["resolved_store"] = context["visited_store"] or context["ms_store"]
            return context
        # Search for store in user stores.
        matches = context["ms_permissions"].filter(store=int(request.session["store"]))
        if matches:
            context["ms_store_permission"] = matches.first()
            context["ms_store"] = context["ms_store_permission"].store
            context["resolved_store"] = context["visited_store"] or context["ms_store"]
            return context
    context["ms_store_permission"] = context["ms_permissions"].first()
    context["ms_store"] = context["ms_store_permission"].store
    context["resolved_store"] = context["visited_store"] or context["ms_store"]
    if has_session:
        request.session["store"] = context["ms_store"].pk
    return context


def get_resolved_store(request) -> typing.Optional[Store]:
    """Get the resolved store for this request."""
    return get_store_context(request)["resolved_store"]


def get_visited_store_id(request) -> typing.Optional[int]:
    """Get the visited store ID for this request."""
    return request.headers.get("X-MS-Store")  # Mobile app sends this header


def get_visited_store(request) -> typing.Optional[Store]:
    """Get the visited store for this request."""
    try:
        return Store.objects.get(id=get_visited_store_id(request))
    except Store.DoesNotExist:
        pass
    return None


def render(request, template, title, context, **kwargs):
    """Render a template."""
    context.update(
        {
            "title": title,
            "current_view": request.resolver_match.view_name,
            "current_sidebar": context.get("sidebar", request.resolver_match.app_name),
            "user": request.user,
            "ms_permissions": request.ms_permissions,
            "ms_store": request.ms_store,
            "ms_store_permission": request.ms_store_permission,
            "ms_next_url": urllib.parse.quote_plus(request.get_full_path(), safe="/"),
        }
    )
    if "current_app" not in context:
        context["current_app"] = request.resolver_match.app_name
    context["ms_extendable_url"] = context["ms_next_url"] + ("&" if request.GET else "?")
    return django.shortcuts.render(request, template, context, **kwargs)


def paginate(object_list, request) -> (django.core.paginator.Paginator, list):
    """Paginate a list of objects."""
    paginator = django.core.paginator.Paginator(object_list, settings.MOBISHOPPER_PAGE_SIZE)
    try:
        page_num = request.GET.get("page", 1)
        page = paginator.get_page(page_num)
    except django.core.paginator.InvalidPage:
        page_num = 1
        page = paginator.get_page(page_num)
    return paginator, page


def store_required(view):
    """Mark a view as requiring a store."""

    @functools.wraps(view)
    def sr_wrapper(request, *args, **kwargs):
        if request.ms_store is None:
            return render(request, "mobishopper/deny_no_stores.html", _("No access to stores"), {}, status=403)
        return view(request, *args, **kwargs)

    return sr_wrapper


def employee_required(function):
    """Mark a view as requiring an employee."""
    return user_passes_test(lambda u: u.is_authenticated and u.is_employee)(function)


def _render_no_access(request):
    """Render a 403 page."""
    return render(request, "mobishopper/deny_perm.html", _("Insufficient permissions"), {}, status=403)


def filter_in_effect(when=None, prefix=""):
    """Filter DateTrackedModels that are currently in effect."""
    if not when:
        when = timezone.now()
    if prefix:
        return (Q(**{prefix + "date_started": None}) | Q(**{prefix + "date_started__lte": when})) & (
            Q(**{prefix + "date_ended": None}) | Q(**{prefix + "date_ended__gt": when})
        )
    else:
        return (Q(date_started=None) | Q(date_started__lte=when)) & (Q(date_ended=None) | Q(date_ended__gt=when))


def filter_in_effect_after(when=None, prefix=""):
    """Filter DateTrackedModels that are currently in effect or will be in effect in the future."""
    if not when:
        when = timezone.now()
    if prefix:
        return Q(**{prefix + "date_ended": None}) | Q(**{prefix + "date_ended__gt": when})
    else:
        return Q(date_ended=None) | Q(date_ended__gt=when)


def filter_given_store(store, prefix=""):
    """Filter objects that are in a given store."""
    if prefix:
        return Q(**{prefix + "store": None}) | Q(**{prefix + "store": store})
    else:
        return Q(store=None) | Q(store=store)


def filter_this_store(request, prefix=""):
    """Filter objects that are in this store."""
    return filter_given_store(request.ms_store, prefix)


def filter_visited_store(request, prefix=""):
    """Filter objects that are in the visited store."""
    return filter_given_store(get_visited_store(request), prefix)


def filter_resolved_store(request, prefix=""):
    """Filter objects that are in the resolved store."""
    return filter_given_store(get_resolved_store(request), prefix)


def filter_visited_store_deals(request):
    """Filter deals that are valid in the visited store."""
    return Q(stores=get_visited_store(request)) | Q(is_global=True)


def filter_this_store_m2m(request):
    """Filter objects that are in this store (for m2m objects)."""
    return Q(stores=request.ms_store)


def filter_this_store_deals_m2m(request):
    """Filter objects that are in this store (for m2m deal objects)."""
    return Q(stores=request.ms_store) | Q(is_global=True)


def filter_in_effect_this_store(request, now=None, prefix=""):
    """Filter objects that are currently in effect in this store."""
    return filter_in_effect(now, prefix) & filter_this_store(request, prefix)


def filter_in_effect_given_store(store, now=None, prefix=""):
    """Filter objects that are currently in effect in the given store."""
    return filter_in_effect(now, prefix) & filter_given_store(store, prefix)


def filter_in_effect_visited_store(request, now=None, prefix=""):
    """Filter objects that are currently in effect in the visited store."""
    return filter_in_effect(now, prefix) & filter_visited_store(request, prefix)


def filter_in_effect_visited_store_deals(request, now=None):
    """Filter objects that are currently in effect in the visited store."""
    return filter_in_effect(now) & filter_visited_store_deals(request)


def filter_in_effect_resolved_store(request, now=None, prefix=""):
    """Filter objects that are currently in effect in the resolved store."""
    return filter_in_effect(now, prefix) & filter_resolved_store(request, prefix)


def filter_in_effect_this_store_m2m(request, now=None):
    """Filter objects that are currently in effect in this store (for m2m objects)."""
    return filter_in_effect(now) & filter_this_store_m2m(request)


def filter_in_effect_this_store_deals_m2m(request, now=None):
    """Filter objects that are currently in effect in this store (for m2m deal objects)."""
    return filter_in_effect(now) & filter_this_store_deals_m2m(request)


def render_delete_get(request, obj, cancel_url, extra_text):
    """Render the standard delete page in the GET version."""
    return render(
        request,
        "mobishopper/confirm_delete.html",
        _("Delete {}").format(obj),
        {"obj": obj, "cancel_url": cancel_url, "hide_title": True, "extra_text": extra_text},
    )


def render_delete(request, obj, success_url, cancel_url, extra_text=""):
    """Render the delete page and handle POST for it."""
    if request.method == "POST" and "confirm" in request.POST:
        obj.delete()
        messages.info(request, _("{} has been deleted.").format(obj))
        return redirect(success_url)
    return render_delete_get(request, obj, cancel_url, extra_text)


def format_money(amount):
    """Format a monetary amount."""
    return f"{amount:.2f}\xa0zł".replace(".", ",")


def format_decimal(num):
    """Format a decimal number."""
    TEN = decimal.Decimal(10)
    if num == 0 or num == int(num):
        return str(int(num))
    for d in range(4):
        mul = num * (TEN ** d)
        if mul == int(mul):
            # Found the correct size without precision loss, format what we've got.
            num_large = str(int(mul)).zfill(d + 1)
            return constants.DECIMAL_SEPARATOR.join((num_large[:-d], num_large[-d:]))
    # Fallback to default implementation
    return str(num).replace(".", constants.DECIMAL_SEPARATOR)
