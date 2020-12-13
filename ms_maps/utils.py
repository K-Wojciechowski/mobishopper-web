"""Utilities for ms_maps views."""
import collections
import logging

import django.utils.timezone
from django.db.models import Count, Q

from ms_baseline.models import Store
from ms_baseline.utils import filter_given_store, filter_in_effect_given_store, filter_in_effect_resolved_store
from ms_maps.models import Aisle, Map, ProductLocation, Subaisle
from ms_products.models import Product

logger = logging.getLogger("ms_maps_utils")


def build_aisles_structure(store: Store, visible_only=True, include_counts=True):
    """Build a structure of aisles."""
    f = filter_given_store(store)
    if visible_only:
        f = f & Q(visible=True)

    aisles = Aisle.objects.filter(f).order_by("name")
    subaisles = Subaisle.objects.filter(f).select_related("parent").order_by("name")
    if include_counts:
        subaisles = subaisles.annotate(
            size=Count("productlocation", filter=filter_in_effect_given_store(store, prefix="productlocation__"))
        )
    subaisle_dict = collections.defaultdict(list)
    for aisle in aisles:
        # Empty aisles
        subaisle_dict[aisle] = []
    for sa in subaisles:
        subaisle_dict[sa.parent].append(sa)

    return sorted(subaisle_dict.items(), key=lambda kv: kv[0].name)


def get_map_in_effect(request, now=None):
    """Get the map currently in effect for a store."""
    try:
        return Map.objects.get(filter_in_effect_resolved_store(request, now))
    except Map.DoesNotExist:
        return None
    except Map.MultipleObjectsReturned:
        logger.error(f"Store {request.ms_store} has multiple maps in effect!")
        return None


def get_missing_product_locations(store, now=None):
    """Get products without locations in a store."""
    if now is None:
        now = django.utils.timezone.now()
    locations = ProductLocation.objects.filter(filter_in_effect_given_store(store, now))
    products_with_locations = Product.objects.filter(productlocation__in=locations)
    products_in_store = Product.objects.filter(filter_in_effect_given_store(store, now))
    return products_in_store.difference(products_with_locations)
