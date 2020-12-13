"""REST API views for ms_products."""
import datetime

import django.utils.timezone
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ms_baseline import constants
from ms_baseline.serializers import SerializerContextMixin, get_serializer_context
from ms_baseline.utils import filter_in_effect_visited_store, filter_visited_store
from ms_products.constants import PREFETCH_PRODUCT_BASIC
from ms_products.models import Product, ProductGroup, Subcategory, Vendor
from ms_products.serializers import (
    ProductBasicSerializer,
    ProductGroupSerializer,
    ProductSerializer,
    SubcategorySerializer,
    VendorSerializer,
)
from ms_products.views.utils import parse_advanced_api_filters


class ProductsList(SerializerContextMixin, generics.ListAPIView):
    """Get the product list for a store."""

    serializer_class = ProductBasicSerializer

    def get_queryset(self):
        """Get the queryset for a product list."""
        filters_list, filters_dict = parse_advanced_api_filters(self.request.query_params)
        return (
            Product.objects.prefetch_related(*PREFETCH_PRODUCT_BASIC)
            .filter(filter_visited_store(self.request), *filters_list, **filters_dict)
            .order_by(*constants.ORDER_NEWEST_FIRST)
        )


class ProductsDetail(SerializerContextMixin, generics.RetrieveAPIView):
    """Get the details of a product."""

    serializer_class = ProductSerializer

    def get_queryset(self):
        """Get the queryset for a product."""
        return Product.objects.filter(filter_visited_store(self.request))


class SubcategoriesList(SerializerContextMixin, generics.ListAPIView):
    """Get a list of subcategories."""

    serializer_class = SubcategorySerializer
    queryset = Subcategory.objects.filter(visible=True)


class VendorsList(SerializerContextMixin, generics.ListAPIView):
    """Get a list of vendors."""

    serializer_class = VendorSerializer

    def get_queryset(self):
        """Get the queryset for a vendor list."""
        extra_filters = {}
        name = self.request.query_params.get("name")
        if name:
            extra_filters["name__icontains"] = name
        return Vendor.objects.filter(filter_in_effect_visited_store(self.request), **extra_filters).order_by("name")


class VendorsDetail(SerializerContextMixin, generics.RetrieveAPIView):
    """Get the details of a vendor."""

    serializer_class = VendorSerializer

    def get_queryset(self):
        """Get the queryset for a vendor."""
        return Vendor.objects.filter(filter_visited_store(self.request))


class VendorsProductsList(SerializerContextMixin, generics.ListAPIView):
    """Get a list of products by a vendor."""

    serializer_class = ProductBasicSerializer

    def get_queryset(self):
        """Get the queryset for a product list."""
        return (
            Product.objects.prefetch_related(*PREFETCH_PRODUCT_BASIC)
            .filter(filter_in_effect_visited_store(self.request), vendor=self.kwargs["pk"])
            .order_by("name")
        )


class ProductGroupsList(SerializerContextMixin, generics.ListAPIView):
    """Get a list of groups."""

    serializer_class = ProductGroupSerializer

    def get_queryset(self):
        """Get the queryset for a product list."""
        filters_list, filters_dict = parse_advanced_api_filters(self.request.query_params, is_product=False)
        return ProductGroup.objects.filter(filter_visited_store(self.request), *filters_list, **filters_dict).order_by(
            *constants.ORDER_NEWEST_FIRST
        )


class ProductGroupsDetail(SerializerContextMixin, generics.RetrieveAPIView):
    """Get the details of a product group."""

    serializer_class = ProductGroupSerializer

    def get_queryset(self):
        """Get the queryset for a product list."""
        return ProductGroup.objects.filter(filter_visited_store(self.request))


@api_view(["GET"])
def bulk_find_products(request):
    """Find multiple products and upgrade them along the way."""
    product_ids = request.query_params.getlist("product")
    products_requested = Product.objects.filter(id__in=product_ids).prefetch_related(*PREFETCH_PRODUCT_BASIC)
    now = django.utils.timezone.now()
    products = []
    new_ids = set()
    upgrades = []
    for p in products_requested:
        current_p = p
        while current_p.replaced_by and not current_p.in_effect(now):
            current_p = current_p.replaced_by
        if current_p.id not in new_ids:
            products.append(current_p)
            new_ids.add(current_p.id)
        if current_p.id != p.id:
            upgrades.append({"old": p.id, "new": current_p.id})

    serializer = ProductBasicSerializer(products, many=True, context=get_serializer_context(request=request))
    return Response(
        {
            "products": serializer.data,
            "upgrades": upgrades,
        }
    )
