"""Template extras for ms_userdata."""

from django import template

register = template.Library()


@register.inclusion_tag("mobishopper/userdata/popular_products_table.html")
def popular_products_table(products):
    """Render the popular products table."""
    return {"products": products}


@register.inclusion_tag("mobishopper/userdata/popular_coupons_table.html")
def popular_coupons_table(coupons):
    """Render the popular coupons table."""
    return {"coupons": coupons}
