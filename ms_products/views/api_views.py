"""API responses for ms_products."""
import typing

import attr
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ms_baseline import vue_models as vm
from ms_baseline.api_utils import asdict_drf_response
from ms_baseline.permission_helpers import permissions_required_products, permissions_required_products_readonly
from ms_baseline.utils import filter_in_effect, filter_in_effect_after, filter_this_store, format_money
from ms_baseline.vue_models import ModalItem, ModalItemContainer
from ms_products import models as m
from ms_products.api_models import build_vue_categories_structure
from ms_products.models import Product, ProductGroup, Vendor

T = typing.TypeVar("T")


def _generate_modal(
    request,
    cls: typing.Type[T],
    name_attr: str,
    converter: typing.Callable[[T], ModalItem],
    *,
    filter_store: bool = True,
    filter_items_in_effect: bool = False,
    filter_items_in_effect_after: bool = True,
):
    queryset = cls.objects.order_by(name_attr)
    if filter_store:
        queryset = queryset.filter(filter_this_store(request))
    if filter_items_in_effect:
        queryset = queryset.filter(filter_in_effect())
    if filter_items_in_effect_after:
        queryset = queryset.filter(filter_in_effect_after())
    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(**{name_attr + "__icontains": query})

    paginator = Paginator(queryset, settings.MOBISHOPPER_MODAL_PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page", 1))
    data = map(converter, page.object_list)
    return JsonResponse(
        attr.asdict(ModalItemContainer(items=list(data), page=page.number, num_pages=paginator.num_pages))
    )


@permissions_required_products_readonly
def list_products_modal(request):
    """Return a list of products for the modal list."""
    return _generate_modal(
        request,
        Product,
        "name",
        lambda p: ModalItem(
            id=p.id,
            name=p.name,
            details_url=reverse("ms_products:show_edit", args=(p.id,)),
            photo=p.photo.url if p.photo else None,
            extras=[p.vendor.name, format_money(p.price)],
        ),
        filter_items_in_effect_after=True,
    )


@permissions_required_products
def list_vendors_modal(request):
    """Return a list of vendors for the modal list."""
    return _generate_modal(
        request,
        Vendor,
        "name",
        lambda v: ModalItem(
            id=v.id,
            name=v.name,
            details_url=reverse("ms_products:vendors_show", args=(v.id,)),
            photo=v.logo.url if v.logo else None,
        ),
        filter_items_in_effect=True,
    )


@permissions_required_products
def list_groups_modal(request):
    """Return a list of vendors for the modal list."""
    return _generate_modal(
        request,
        ProductGroup,
        "name",
        lambda g: ModalItem(
            id=g.id,
            name=g.name,
            details_url=reverse("ms_products:groups_show", args=(g.id,)),
            photo=g.photo.url if g.photo else None,
        ),
    )


@api_view()
def get_standard_meta_fields(request, subcategory: typing.Optional[int] = None):
    """Return a list of standard meta fields for a given subcategory (or for all subcategories)."""
    if subcategory:
        fields = m.StandardMetaField.objects.filter(
            Q(subcategories_required=subcategory) | Q(subcategories_recommended=subcategory)
        )
    else:
        fields = m.StandardMetaField.objects.all()

    vue_fields = [vm.StandardMetaField.from_db(s, subcategory) for s in fields]
    return asdict_drf_response(vm.StandardMetaFieldContainer(items=vue_fields, subcategory=subcategory))


@api_view()
def categories_structure(request):
    """Get the categories structure."""
    categories = build_vue_categories_structure()
    return Response([attr.asdict(c) for c in categories])
