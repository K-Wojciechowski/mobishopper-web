"""REST API views for ms_deals."""
import datetime
import typing

import django.utils.timezone
import rest_framework.exceptions
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins
from rest_framework.decorators import api_view
from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from rest_framework.settings import api_settings as _drf_api_settings

from ms_baseline import constants
from ms_baseline.serializers import SerializerContextMixin, get_serializer_context
from ms_baseline.utils import filter_in_effect_visited_store_deals, get_visited_store
from ms_deals.models import Coupon, CouponSet, Deal
from ms_deals.serializers import CouponSerializer, CouponSetSerializer, DealSerializer
from ms_userdata.models import CouponSetUse, CouponUse


@api_view()
def deals_all_list(request):
    """Get a list of all deals."""
    deals = Deal.objects.filter(filter_in_effect_visited_store_deals(request)).order_by("name")
    coupons = Coupon.objects.filter(filter_in_effect_visited_store_deals(request)).order_by("name")
    coupon_sets = CouponSet.objects.filter(filter_in_effect_visited_store_deals(request)).order_by("name")

    context = get_serializer_context(request=request)

    out = []
    out += [CouponSetSerializer(cs, context=context).data for cs in coupon_sets]
    out += [CouponSerializer(c, context=context).data for c in coupons]
    out += [DealSerializer(d, context=context).data for d in deals]

    paginator: BasePagination = _drf_api_settings.DEFAULT_PAGINATION_CLASS()
    paginated = paginator.paginate_queryset(out, request)
    return paginator.get_paginated_response(paginated)


@api_view()
def coupons_usable(request, pk):
    """Check if a coupon is usable."""
    return _get_coupons_usable(request, Coupon, pk)


@api_view()
def coupon_sets_usable(request, pk):
    """Check if a coupon set is usable."""
    return _get_coupons_usable(request, CouponSet, pk)


class DealsList(SerializerContextMixin, generics.ListAPIView):
    """Get the deals list for a store."""

    serializer_class = DealSerializer

    def get_queryset(self):
        """Get the queryset for a product list."""
        return Deal.objects.filter(filter_in_effect_visited_store_deals(self.request)).order_by("name")


class DealsDetail(SerializerContextMixin, generics.RetrieveAPIView):
    """Get the details of a deal."""

    serializer_class = DealSerializer

    def get_queryset(self):
        """Get the queryset for a product."""
        return Deal.objects.filter(filter_in_effect_visited_store_deals(self.request))


class CouponsList(SerializerContextMixin, generics.ListAPIView):
    """Get the coupons list for a store."""

    serializer_class = CouponSerializer

    def get_queryset(self):
        """Get the queryset for a product list."""
        return Coupon.objects.filter(filter_in_effect_visited_store_deals(self.request)).order_by("name")


class CouponsDetail(SerializerContextMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):
    """Get the details of a coupon or use a coupon."""

    serializer_class = CouponSerializer

    def get_queryset(self):
        """Get the queryset for a product."""
        return Coupon.objects.filter(filter_in_effect_visited_store_deals(self.request))

    def post(self, request, pk, *args, **kwargs):
        """Use a coupon."""
        return _generate_coupon_coupon_set_qr(self.request, self.get_object(), CouponUse)


class CouponSetsList(SerializerContextMixin, generics.ListAPIView):
    """Get the coupon sets list for a store."""

    serializer_class = CouponSetSerializer

    def get_queryset(self):
        """Get the queryset for a product list."""
        return CouponSet.objects.filter(filter_in_effect_visited_store_deals(self.request)).order_by("name")


class CouponSetsDetail(SerializerContextMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):
    """Get the details of a coupon set or use a coupon set."""

    serializer_class = CouponSetSerializer

    def get_queryset(self):
        """Get the queryset for a product."""
        return CouponSet.objects.filter(filter_in_effect_visited_store_deals(self.request))

    def post(self, request, pk, *args, **kwargs):
        """Use a coupon set."""
        return _generate_coupon_coupon_set_qr(self.request, self.get_object(), CouponSetUse)


def _get_coupons_usable(request, coupon_class: typing.Union[typing.Type[Coupon], typing.Type[CouponSet]], pk: int):
    """Get the coupons usable response."""
    coupon = get_object_or_404(coupon_class, id=pk)
    usable, reason = coupon.is_usable(request.user)
    res = {"id": pk, "usable": usable}
    if reason:
        res["reason"] = reason
    return Response(res)


def _generate_coupon_coupon_set_qr(
    request,
    coupon: typing.Union[Coupon, CouponSet],
    use_class: typing.Union[typing.Type[CouponUse], typing.Type[CouponSetUse]],
):
    """Generate a Coupon/CouponSet QR code."""
    now = django.utils.timezone.now()
    usable, reason = coupon.is_usable(request.user, now)
    if not usable and reason == "require_account":
        raise rest_framework.exceptions.NotAuthenticated()
    elif not usable:
        raise rest_framework.exceptions.PermissionDenied(reason)

    use: typing.Union[CouponUse, CouponSetUse, None] = (
        use_class.objects.filter(user=request.user, coupon=coupon).order_by("valid_until").last()
    )

    if use is not None and not use.is_still_valid(now):
        raise rest_framework.exceptions.PermissionDenied("one_use")
    elif not use:
        coupon_user = request.user if request.user.is_authenticated else None
        valid_until = now + datetime.timedelta(minutes=constants.COUPON_USE_VALIDITY_MINUTES)
        use = use_class(user=coupon_user, coupon=coupon, store=get_visited_store(request), valid_until=valid_until)
        use.save()
    return Response({"data": coupon.generate_coupon_qr_data(use), "valid_until": use.valid_until})
