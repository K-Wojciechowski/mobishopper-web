"""Utilities for ms_products views."""
import collections
import datetime
import json
import typing

import django.utils.timezone
from django.db.models import Count, Q

from ms_baseline.utils import filter_in_effect, filter_this_store
from ms_products import forms
from ms_products.models import Category, Product, Subcategory

T = typing.TypeVar("T")


def get_global_upcoming_recent(now=None):
    """Get global upcoming and recent products."""
    if not now:
        now = django.utils.timezone.now()
    now_minus_3 = now - datetime.timedelta(days=3)
    now_plus_7 = now + datetime.timedelta(days=7)

    return {
        "products_global_upcoming": Product.objects.filter(date_started__gt=now, date_started__lt=now_plus_7)
        .filter(store=None)
        .order_by("-date_started", "-date_modified"),
        "products_global_recent": Product.objects.filter(
            (Q(date_started__gt=now_minus_3) & Q(date_started__lt=now))
            | (Q(date_started=None) & Q(date_added__gt=now_minus_3))
        )
        .filter(store=None)
        .order_by("-date_started", "-date_modified"),
    }


def get_local_upcoming_recent(request, now=None):
    """Get local upcoming and recent products."""
    if not now:
        now = django.utils.timezone.now()
    now_minus_3 = now - datetime.timedelta(days=3)
    now_plus_7 = now + datetime.timedelta(days=7)

    return {
        "products_local_upcoming": Product.objects.filter(date_started__gt=now, date_started__lt=now_plus_7)
        .filter(filter_this_store(request))
        .order_by("-date_started", "-date_modified"),
        "products_local_recent": Product.objects.filter(
            (Q(date_started__gt=now_minus_3) & Q(date_started__lt=now))
            | (Q(date_started=None) & Q(date_added__gt=now_minus_3))
        )
        .filter(filter_this_store(request))
        .order_by("-date_started", "-date_modified"),
    }


def build_subcat_menu(visible_only=True):
    """Build a menu of subcategories."""
    if visible_only:
        filters = {"visible": True}
    else:
        filters = {}

    subcategories = Subcategory.objects.filter(**filters).select_related("parent").order_by("name")
    subcat_dict = collections.defaultdict(list)
    for sc in subcategories:
        subcat_dict[sc.parent.name].append(sc)
    return sorted(subcat_dict.items())


def build_categories_structure(visible_only=True, include_counts=True):
    """Build a structure of categories."""
    if visible_only:
        filters = {"visible": True}
    else:
        filters = {}

    categories = Category.objects.filter(**filters).order_by("name")
    subcategories = Subcategory.objects.filter(**filters).select_related("parent").order_by("name")
    if include_counts:
        subcategories = subcategories.annotate(size=Count("product", filter=filter_in_effect(prefix="product__")))
    subcat_dict = collections.defaultdict(list)
    for cat in categories:
        # Empty categories
        subcat_dict[cat] = []
    for sc in subcategories:
        subcat_dict[sc.parent].append(sc)

    return sorted(subcat_dict.items(), key=lambda kv: kv[0].name)


def parse_advanced_search_filters(
    request, form_data: typing.Mapping[str, typing.Union[str, typing.List[str]]]
) -> (typing.Dict[str, typing.Any], typing.List[typing.Any]):
    """Parse advanced search filters for a product or a product group."""
    filters = {}
    filters_list = []

    if form_data.get("name"):
        filters["name" + "__icontains"] = form_data.get("name")
    if form_data.get("description"):
        filters["description" + "__icontains"] = form_data.get("description")
    if form_data.get("vendor"):
        filters["vendor__name" + "__icontains"] = form_data.get("vendor")

    if form_data.get("subcategories"):
        filters["subcategory__in"] = [int(cat) for cat in form_data["subcategories"] if cat != "-1"]

    if form_data.get("is_group"):  # Optional in group search
        filters["group__isnull"] = False

    if form_data.get("is_store"):
        filters["store__isnull"] = False
    else:
        filters_list.append(filter_this_store(request))

    if form_data.get("extra_metadata_raw"):
        meta_raw = json.loads(form_data["extra_metadata_raw"])
        meta_dict = Product.build_extra_metadata_dict_from_raw(meta_raw)
        for k, v in meta_dict.items():
            filters[f"extra_metadata_dict__{k}__icontains"] = v

    if form_data["valid_at"]:
        filters_list.append(filter_in_effect(form_data["valid_at"]))

    return filters_list, filters


def parse_advanced_api_filters(
    form_data: typing.Mapping[str, typing.Union[str, typing.List[str]]],
    *,
    is_product: bool = True,
    ignore_vendor: bool = False,
) -> (typing.Dict[str, typing.Any], typing.List[typing.Any]):
    """Parse advanced search filters for a product or a product group."""
    filters = {}
    filters_list = []

    if form_data.get("name"):
        filters["name" + "__icontains"] = form_data.get("name")
    if form_data.get("description"):
        filters["description" + "__icontains"] = form_data.get("description")
    if form_data.get("vendor") and not ignore_vendor:
        filters["vendor__name" + "__icontains"] = form_data.get("vendor")

    if form_data.get("subcategories"):
        filters["subcategory__in"] = [int(cat) for cat in form_data["subcategories"] if cat != "-1"]

    if form_data.get("meta") and is_product:
        meta_raw = json.loads(form_data["meta"])
        meta_dict = Product.build_extra_metadata_dict_from_raw(meta_raw)
        for k, v in meta_dict.items():
            filters[f"extra_metadata_dict__{k}__icontains"] = v

    if form_data.get("recent_upcoming", "").lower() in ("1", "true"):
        now = django.utils.timezone.now()
        now_minus_3 = now - datetime.timedelta(days=3)
        now_plus_7 = now + datetime.timedelta(days=7)
        filters_list.append(
            (Q(date_started__gt=now_minus_3) | (Q(date_started=None) & Q(date_added__gt=now_minus_3)))
            & (Q(date_ended=None) | Q(date_ended__gt=now))
        )
        filters_list.append(
            ((Q(date_started=None) & Q(date_added__lt=now_plus_7)) | Q(date_started__lt=now_plus_7))
            & (Q(date_ended=None) | Q(date_ended__gt=now))
        )
    else:
        filters_list.append(filter_in_effect())

    return filters_list, filters


def handle_product_filters(
    request,
    form_class: typing.Type[forms.ProductGenericFilterForm],
    model_class: typing.Type[T],
    filter_store: bool = True,
) -> (forms.ProductGenericFilterForm, bool, typing.Iterable[T], str):
    """Handle filters for products or product groups."""
    form = form_class(request.GET)
    if form.is_valid():
        filtering_error = False
        filters_list, filters = parse_advanced_search_filters(request, form.cleaned_data)
    else:
        filtering_error = True
        filters_list, filters = [filter_in_effect(), filter_this_store(request)], {}

    if filter_store and request.ms_store is not None:
        filters_list.append(filter_this_store(request))
    elif filter_store and "store__isnull" not in filters and "store" not in filters:
        filters["store"] = None

    # Default to displaying currently valid things
    if "valid_at" not in request.GET:
        filters_list.append(filter_in_effect())

    order = request.GET.get("order", "name")

    return form, filtering_error, model_class.objects.filter(*filters_list, **filters).order_by(order), order
