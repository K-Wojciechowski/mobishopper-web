"""Template extras for ms_maps."""
from django import template

register = template.Library()


@register.inclusion_tag("mobishopper/maps/aisle_form.html")
def aisle_form(form):
    """Render a aisle form."""
    return {"form": form}


@register.inclusion_tag("mobishopper/maps/subaisle_form.html")
def subaisle_form(form, copy_global=None, run_js=False):
    """Render a subaisle form."""
    return {"form": form, "run_js": run_js, "copy_global": copy_global}
