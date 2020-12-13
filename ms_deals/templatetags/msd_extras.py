"""Template extras for ms_deals."""
from django import template

register = template.Library()


@register.inclusion_tag("mobishopper/deals/deals_search_form.html")
def deals_search_form(search_form, is_coupon_set=False):
    """Render a deals search form."""
    return {"search_form": search_form, "is_coupon_set": is_coupon_set}


@register.inclusion_tag("mobishopper/deals/deals_table.html")
def deals_table(page, request, show_order, is_coupon_set=False):
    """Render a deals table."""
    return {"page": page, "request": request, "show_order": show_order, "is_coupon_set": is_coupon_set}
