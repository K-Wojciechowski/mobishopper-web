"""Checkout API views."""
import base64
import logging
import typing

import django.utils.timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response

from ms_baseline.models import CheckoutApiKey
from ms_deals.models import Coupon, CouponSet
from ms_deals.serializers import CouponSerializer, CouponSetSerializer
from ms_userdata.models import CouponSetUse, CouponUse

LOGGER = logging.getLogger(__name__)

COUPON_CLASSES = {"c": Coupon, "s": CouponSet}
USE_CLASSES = {"c": CouponUse, "s": CouponSetUse}


class IsCheckoutApiAuthenticated(BasePermission):
    """Allows access only to Checkout API users."""

    def has_permission(self, request, view):
        """Check if the request is allowed."""
        api_key = request.headers.get("X-MS-Checkout-API-Key", "")
        try:
            key_object = CheckoutApiKey.objects.get(is_active=True, key=api_key)
        except Exception:
            key_object = None
        request.api_key = key_object
        return request.api_key is not None


@api_view(["POST"])
@permission_classes([IsCheckoutApiAuthenticated])
def checkout_coupon(request: Request):
    """Use a coupon at checkout."""
    coupon_code_raw = request.data.get("code")
    if not coupon_code_raw:
        return Response({"success": False, "error": "request_invalid"}, status=400)

    try:
        coupon_code: str = base64.b64decode(coupon_code_raw).decode("utf-8")
        prefix, coupon_key, user, use_key = coupon_code.split(".")
        coupon_cls: typing.Union[typing.Type[Coupon], typing.Type[CouponSet]] = COUPON_CLASSES[prefix]
        use_cls: typing.Union[typing.Type[CouponUse], typing.Type[CouponSetUse]] = USE_CLASSES[prefix]

        try:
            use: typing.Union[CouponUse, CouponSetUse] = use_cls.objects.get(uuid=use_key)
        except (CouponUse.DoesNotExist, CouponSetUse.DoesNotExist):
            return Response({"success": False, "error": "coupon_not_found"}, status=404)

        try:
            coupon: typing.Union[Coupon, CouponSet] = coupon_cls.objects.get(uuid=coupon_key)
        except (CouponUse.DoesNotExist, CouponSetUse.DoesNotExist):
            return Response({"success": False, "error": "coupon_not_found"}, status=404)

        if (isinstance(use, CouponUse) and use.coupon_id != coupon.id) or (
            isinstance(use, CouponSetUse) and use.coupon_set_id != coupon.id
        ):
            return Response({"success": False, "error": "coupon_tampered_with"}, status=403)

        if use.is_used:
            return Response({"success": False, "error": "coupon_already_used"}, status=403)

        if not use.is_still_valid():
            return Response({"success": False, "error": "coupon_expired"}, status=403)

        use.is_used = True
        use.used_date = django.utils.timezone.now()
        use.used_with = request.api_key
        use.save()

        serializer_context = {"request": request, "store_id": request.api_key.store.id}

        if isinstance(coupon, Coupon):
            type_name = "COUPON"
            coupon_data = CouponSerializer(coupon, context=serializer_context).data
        elif isinstance(coupon, Coupon):
            type_name = "COUPON_SET"
            coupon_data = CouponSetSerializer(coupon, context=serializer_context).data
        else:
            return Response({"success": False, "error": "internal_error"}, status=500)

        return Response({"success": True, "type": type_name, "data": coupon_data})

    except Exception as e:
        LOGGER.exception("Request to checkout_coupon failed", e)
        return Response({"success": False, "error": "coupon_invalid"}, status=400)
