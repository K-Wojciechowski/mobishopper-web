"""MobiShopper baseline views."""
import datetime

import django.utils.timezone
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.utils.translation import gettext as _

from ms_baseline import constants
from ms_baseline.models import MsUser, Store, UserStorePermission
from ms_baseline.utils import (
    employee_required,
    filter_in_effect,
    filter_in_effect_this_store,
    filter_in_effect_this_store_m2m,
    filter_this_store,
    render,
)
from ms_deals.models import Coupon, Deal
from ms_maps.models import ProductLocation
from ms_products.models import Product
from ms_userdata.models import CouponUse, ShoppingList


def landing_page(request):
    """Show the landing page."""
    return render(request, "mobishopper/landing.html", "", {"mask": settings.MOBISHOPPER_MASK_LANDING})


@employee_required
def management_home(request):
    """Show the home page."""
    now = django.utils.timezone.now()
    now_minus_7d = now - datetime.timedelta(days=7)
    product_count = Product.objects.filter(filter_in_effect(now)).count()
    if request.ms_store:
        products_in_store = Product.objects.filter(filter_in_effect_this_store(request, now))
        locations = ProductLocation.objects.filter(filter_in_effect_this_store(request, now))
        products_with_locations = Product.objects.filter(productlocation__in=locations)
        products_without_location = products_in_store.difference(products_with_locations).count()
        deals_coupons = (
            Deal.objects.filter(filter_in_effect_this_store_m2m(request, now)).count()
            + Coupon.objects.filter(filter_in_effect_this_store_m2m(request, now)).count()
        )
        coupons_7d = CouponUse.objects.filter(filter_this_store(request), date_added__gt=now_minus_7d).count()
        shopping_lists_7d = ShoppingList.objects.filter(filter_this_store(request), date_added__gt=now_minus_7d).count()
        context = {
            "product_count": product_count,
            "products_in_store": products_in_store.count(),
            "products_without_location": products_without_location,
            "deals_coupons": deals_coupons,
            "coupons_7d": coupons_7d,
            "shopping_lists_7d": shopping_lists_7d,
        }
    else:
        user_count = MsUser.objects.count()
        store_count = Store.objects.filter(hidden=False).count()
        deals_coupons = (
            Deal.objects.filter(filter_in_effect(now)).count() + Coupon.objects.filter(filter_in_effect(now)).count()
        )
        shopping_lists_7d = ShoppingList.objects.filter(date_added__gt=now_minus_7d).count()
        coupons_7d = CouponUse.objects.filter(date_added__gt=now_minus_7d).count()

        context = {
            "product_count": product_count,
            "user_count": user_count,
            "store_count": store_count,
            "deals_coupons": deals_coupons,
            "coupons_7d": coupons_7d,
            "shopping_lists_7d": shopping_lists_7d,
        }
    return render(request, "mobishopper/home.html", _("Home"), context)


@employee_required
def change_store(request, sid: int):
    """Change the current store."""
    if sid == 0:
        request.session["store"] = ""
    else:
        try:
            _usp = UserStorePermission.objects.get(user=request.user, store=sid)
            request.session["store"] = sid
        except UserStorePermission.DoesNotExist:
            return HttpResponseForbidden()

    return HttpResponseRedirect(request.GET["next"])


@employee_required
def my_permissions(request):
    """View user’s permissions."""
    return render(
        request,
        "mobishopper/my_permissions.html",
        _("My permissions"),
        {"local_permissions_short_titles": constants.LOCAL_PERMISSIONS_SHORT_TITLES},
    )
