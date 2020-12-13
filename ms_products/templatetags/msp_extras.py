"""Template extras for ms_products."""
import typing

from django import template
from django.utils.translation import gettext as _

import ms_products.views.utils

if typing.TYPE_CHECKING:
    import ms_products.forms
    import ms_products.models

register = template.Library()


@register.inclusion_tag("mobishopper/products/products_table.html", takes_context=True)
def products_table(context: dict, products: typing.Iterable, show_order: bool = False) -> dict:
    """Render the products table."""
    pt_context = {"products": products, "show_order": show_order}
    if "order" in context:
        pt_context["order"] = context["order"]
    return pt_context


@register.inclusion_tag("mobishopper/products/product_history_data.html")
def product_history_data(product: "ms_products.models.Product") -> dict:
    """Show product data for the history page."""
    return {"product": product}


@register.inclusion_tag("mobishopper/products/products_add_edit_form.html", takes_context=True)
def product_add_edit_form(
    context: dict,
    form: typing.Union[ms_products.forms.ProductAddForm, ms_products.forms.ProductEditForm],
    product: "typing.Optional[ms_products.models.Product]",
    action_input=False,
) -> dict:
    """Show a form for adding or editing products."""
    vendor_name = product.vendor.name if product and product.vendor else ""
    group_name = product.group.name if product and product.group else ""
    return {
        "form": form,
        "action_input": action_input,
        "vendor_name": vendor_name,
        "group_name": group_name,
        "request": context["request"],
    }


@register.inclusion_tag("mobishopper/products/subcat_menu_field.html")
def subcat_menu_field(
    form, *, multiple, required, field_name=None, show_blank=None, field_title=None, visible_only=True
):
    """Show the subcategories menu."""
    if field_name is None:
        field_name = "subcategories" if multiple else "subcategory"
    form_field = form.fields[field_name].get_bound_field(form, field_name)
    subcat_menu = ms_products.views.utils.build_subcat_menu(visible_only)
    if field_title is None:
        field_title = _("Subcategories") if multiple else _("Subcategory")
    elif field_title == "_form":
        field_title = form_field.label
    if show_blank is None:
        show_blank = not multiple
    checked_ids = []
    if form_field.initial is not None:
        checked_items = form_field.initial if isinstance(form_field.initial, list) else [form_field.initial]
        if checked_items:
            if isinstance(checked_items[0], int):
                checked_ids = checked_items
            else:
                checked_ids = [i.id for i in checked_items]
    return {
        "field_title": field_title,
        "form_field": form_field,
        "show_blank": show_blank,
        "multiple": multiple,
        "required": required,
        "subcat_menu": subcat_menu,
        "checked_ids": checked_ids,
    }
