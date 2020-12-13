"""Template extras for MobiShopper."""
import copy

import django.utils.html
from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from ms_baseline.utils import format_decimal, format_money

register = template.Library()


def _set_visibility(item, usp, user):
    """Set visibility of a menu/sidebar item."""
    item["visible"] = False
    iperm = item.get("perm")
    gperm = item.get("gperm")
    xperm = item.get("xperm")
    if xperm:
        item["visible"] = getattr(user, xperm)
    elif usp and iperm:
        if iperm != "":
            item["visible"] = getattr(usp, iperm)
    elif not usp and gperm:
        if gperm == "":
            item["visible"] = False
        elif isinstance(gperm, str):
            item["visible"] = getattr(user, gperm)
        else:
            item["visible"] = any(getattr(user, p) for p in gperm)
    elif iperm is None and gperm is None:
        item["visible"] = True


@register.inclusion_tag("mobishopper/extras/menu.html", takes_context=True)
def render_menu(context):
    """Render the site menu."""
    menu = settings.MOBISHOPPER_MENU.copy()
    usp = context["ms_store_permission"]
    user = context["user"]
    for item in menu:
        _set_visibility(item, usp, user)

    return {"menu": menu, "current_app": context.get("current_app", "")}


@register.inclusion_tag("mobishopper/extras/sidebar.html", takes_context=True)
def render_sidebar(context):
    """Render the sidebar."""
    sidebar = copy.deepcopy(settings.MOBISHOPPER_SIDEBAR[context["current_sidebar"]])
    usp = context["ms_store_permission"]
    user = context["user"]
    for group in sidebar["groups"]:
        _set_visibility(group, usp, user)
        for item in group["items"]:
            _set_visibility(item, usp, user)
    return {"sidebar": sidebar, "current_view": context.get("current_view", "")}


@register.inclusion_tag("mobishopper/extras/validity_text.html")
def validity_text(obj):
    """Show an object’s validity as text."""
    return {"date_started": obj.date_started, "date_ended": obj.date_ended}


@register.inclusion_tag("mobishopper/extras/paginator.html", takes_context=True)
def paginator(context, page):
    """Render a pager."""
    return {"page": page, "ms_extendable_url": context["ms_extendable_url"]}


@register.inclusion_tag("mobishopper/extras/show_all_chooser.html")
def show_all_chooser(show_all, only_valid=True):
    """Render a widget to choose between all items or only valid/visible."""
    return {"show_all": show_all, "only_valid": only_valid}


@register.simple_tag
def bsicon(name: str, wh: int) -> django.utils.html.SafeString:
    """Render a Bootstrap Icon."""
    return format_html(
        '<svg class="bi" width="{1}" height="{1}" fill="currentColor">'
        '<use xlink:href="/static/bootstrap-icons.svg#{0}"/></svg>',
        name,
        wh,
    )


@register.simple_tag
def bsiconbox_raw(name: str, wh: int, text: str) -> django.utils.html.SafeString:
    """Render a Bootstrap Icon with untranslated text."""
    return format_html('<span class="iconbox">{0} {1}</span>', bsicon(name, wh), text)


@register.simple_tag
def bsiconbox(name: str, wh: int, text: str) -> django.utils.html.SafeString:
    """Render a Bootstrap Icon with translated text."""
    return bsiconbox_raw(name, wh, _(text))


@register.simple_tag
def bsiconbox_right_raw(name: str, wh: int, text: str) -> django.utils.html.SafeString:
    """Render a Bootstrap Icon with untranslated text on the right side."""
    return format_html('<span class="iconbox">{1} {0}</span>', bsicon(name, wh), text)


@register.simple_tag
def bsiconbox_right(name: str, wh: int, text: str) -> django.utils.html.SafeString:
    """Render a Bootstrap Icon with translated text on the right side."""
    return bsiconbox_right_raw(name, wh, _(text))


@register.simple_tag
def buttonbox_save():
    """Display a button box with a save button."""
    return format_html(
        '<div class="buttonbox"><button type="submit" class="btn btn-lg btn-primary">{0}</button></div>',
        bsiconbox("check", 20, "Save"),
    )


@register.simple_tag
def inline_form_field(field):
    """Render an inline form field."""
    return format_html('<label class="sr-only" for="{0}">{1}</label>{2}', field.id_for_label, field.label, field)


@register.simple_tag
def check_radio_field(field):
    """Render a checkbox or radio box."""
    return format_html(
        '<div class="form-check"><label for="{0}">{1}&nbsp;{2}</label></div>', field.id_for_label, field, field.label
    )


@register.inclusion_tag("mobishopper/extras/copy_get_if.html")
def start_copy_get_if(condition, request):
    """Start copying GET items if condition is met."""
    return {"condition": condition, "request": request}


@register.simple_tag
def close_copy_get_if(cond):
    """End copying GET items if condition is met. Place at the end of the page."""
    return mark_safe("</form>" if cond else "")


@register.simple_tag
def money(value):
    """Format a monetary value."""
    return format_money(value)


@register.simple_tag(name="format_decimal")
def format_decimal_(value):
    """Format a decimal value."""
    return format_decimal(value)


@register.simple_tag
def no_results_msg():
    """Display a “No results” message."""
    return format_html('<p class="lead">{0}</p>', _("No results found."))


@register.simple_tag
def bool_yesno(value: bool) -> str:
    """Display a boolean value as “yes” or “no”."""
    return _("yes") if value else _("no")


@register.simple_tag(takes_context=True)
def table_ord_helper(context: dict, description: str, name: str, is_default: bool = False) -> str:
    """Display ordering buttons in tables."""
    if not context.get("show_order"):
        return _(description)
    new_order = name
    icon = "caret-right"
    mname = "-" + name
    order = context.get("order", name if is_default else None)
    if order == name:
        icon = "caret-up-fill"
        new_order = mname
    elif order == mname:
        icon = "caret-down-fill"

    return format_html(
        '<button type="submit" class="table-header-btn" name="order" value="{0}">{1}</button>',
        new_order,
        bsiconbox_right(icon, 12, description),
    )


@register.inclusion_tag("mobishopper/extras/modal_item_selector.html")
def modal_item_selector(field, js_id: str, fallback: str):
    """Render a modal item selector."""
    return {"field": field, "js_id": js_id, "fallback": fallback}
