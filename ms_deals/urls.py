"""URL configuration for ms_deals."""
from django.urls import path

from ms_deals import views


def blank(request):
    """Blank."""
    pass


app_name = "ms_deals"
urlpatterns = [
    path("", views.deals_overview, name="deals_overview"),
    path("deals/", views.deals_list, name="deals_list"),
    path("deals/store/", views.deals_list_store, name="deals_list_store"),
    path("deals/add/", views.deals_add, name="deals_add"),
    path("deals/<int:id>/", views.deals_show_edit, name="deals_show_edit"),
    path("coupons/", views.coupons_list, name="coupons_list"),
    path("coupons/add/", views.coupons_add, name="coupons_add"),
    path("coupons/<int:id>/", views.coupon_show_edit, name="coupons_show_edit"),
    path("coupon-sets/", views.coupon_sets_list, name="coupon_sets_list"),
    path("coupon-sets/add/", views.coupon_sets_add, name="coupon_sets_add"),
    path("coupon-sets/<int:id>/", views.coupon_sets_show_edit, name="coupon_sets_show_edit"),
]
