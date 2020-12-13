"""Views for ms_userdata."""
import datetime

import django.utils.timezone
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

from ms_baseline.permission_helpers import permissions_required_stats
from ms_baseline.utils import filter_this_store, filter_this_store_deals_m2m, paginate, render
from ms_deals.models import Coupon
from ms_products.models import Product
from ms_userdata.models import CouponUse, ShoppingList


def _get_popular_products(request, now=None):
    """Get a queryset of popular products."""
    if now is None:
        now = django.utils.timezone.now()
    now_minus_7d = now - datetime.timedelta(days=7)
    now_minus_24h = now - datetime.timedelta(hours=24)
    return (
        Product.objects.filter(filter_this_store(request))
        .annotate(
            last_7d=Count("shoppinglistentry", filter=Q(shoppinglistentry__date_added__gt=now_minus_7d)),
            last_24h=Count("shoppinglistentry", filter=Q(shoppinglistentry__date_added__gt=now_minus_24h)),
        )
        .filter(last_7d__gt=0)
        .order_by("-last_7d", "name")
    )


def _get_popular_coupons(request, now=None):
    """Get a queryset of popular coupons."""
    if now is None:
        now = django.utils.timezone.now()
    now_minus_7d = now - datetime.timedelta(days=7)
    now_minus_24h = now - datetime.timedelta(hours=24)
    return (
        Coupon.objects.filter(filter_this_store_deals_m2m(request))
        .annotate(
            last_7d=Count("couponuse", filter=Q(date_added__gt=now_minus_7d)),
            last_24h=Count("couponuse", filter=Q(date_added__gt=now_minus_24h)),
        )
        .filter(last_7d__gt=0)
        .order_by("-last_7d", "name")
    )


@permissions_required_stats
def stats_overview(request):
    """Show an overview of statistics."""
    now = django.utils.timezone.now()
    now_minus_7d = now - datetime.timedelta(days=7)
    now_minus_24h = now - datetime.timedelta(hours=24)
    if request.ms_store:
        coupons_24h = CouponUse.objects.filter(filter_this_store(request), date_added__gt=now_minus_24h).count()
        shopping_lists_24h = ShoppingList.objects.filter(
            filter_this_store(request), date_added__gt=now_minus_24h
        ).count()
        coupons_7d = CouponUse.objects.filter(filter_this_store(request), date_added__gt=now_minus_7d).count()
        shopping_lists_7d = ShoppingList.objects.filter(filter_this_store(request), date_added__gt=now_minus_7d).count()
    else:
        coupons_24h = CouponUse.objects.filter(date_added__gt=now_minus_24h).count()
        shopping_lists_24h = ShoppingList.objects.filter(date_added__gt=now_minus_24h).count()
        coupons_7d = CouponUse.objects.filter(date_added__gt=now_minus_7d).count()
        shopping_lists_7d = ShoppingList.objects.filter(date_added__gt=now_minus_7d).count()

    products_list = _get_popular_products(request, now)[:10]
    coupons_list = _get_popular_coupons(request, now)[:10]

    context = {
        "coupons_7d": coupons_7d,
        "shopping_lists_7d": shopping_lists_7d,
        "coupons_24h": coupons_24h,
        "shopping_lists_24h": shopping_lists_24h,
        "products_list": products_list,
        "coupons_list": coupons_list,
    }

    return render(request, "mobishopper/userdata/stats_overview.html", _("Statistics"), context)


def popular_coupons(request):
    """Show a list of popular coupons."""
    qs = _get_popular_coupons(request)
    paginator, page = paginate(qs, request)
    context = {"paginator": paginator, "page": page}
    return render(request, "mobishopper/userdata/popular_coupons.html", _("Popular coupons"), context)


def popular_products(request):
    """Show a list of popular products."""
    qs = _get_popular_products(request)
    paginator, page = paginate(qs, request)
    context = {"paginator": paginator, "page": page}
    return render(request, "mobishopper/userdata/popular_products.html", _("Popular products"), context)


def shared_list(request, uuid):
    """Show a shared list in the app."""
    shopping_list = get_object_or_404(ShoppingList, sharing_uuid=uuid)
    entries = shopping_list.entries.order_by("product__name").all()
    owner = shopping_list.user.get_full_name()
    return render(
        request,
        "mobishopper/userdata/shared_shopping_list.html",
        _("Shopping list {0}").format(shopping_list.name),
        {"shopping_list": shopping_list, "shopping_list_entries": entries, "owner": owner},
    )


def accept_invite(request, uuid):
    """Accept a shoppping list invite."""
    link = f"mobishopper://invite/{uuid}"
    return render(request, "mobishopper/mobile_redirect.html", _("Launching MobiShopper…"), {"link": link})
