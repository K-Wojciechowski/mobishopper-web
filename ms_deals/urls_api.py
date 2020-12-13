"""URL configuration for ms_deals (API)."""
from django.urls import path

from ms_deals.views import api_views, rest_views

app_name = "ms_deals_api"
urlpatterns = [
    path("coupons-modal/", api_views.list_coupons_modal, name="coupons_modal"),
    path("", rest_views.deals_all_list, name="deals_all"),
    path("deals/", rest_views.DealsList.as_view(), name="deals_list"),
    path("deals/<int:pk>/", rest_views.DealsDetail.as_view(), name="deals_details"),
    path("coupons/", rest_views.CouponsList.as_view(), name="coupons_list"),
    path("coupons/<int:pk>/", rest_views.CouponsDetail.as_view(), name="coupons_details"),
    path("coupons/<int:pk>/usable/", rest_views.coupons_usable, name="coupons_usable"),
    path("coupon-sets/", rest_views.CouponSetsList.as_view(), name="coupon_sets_list"),
    path("coupon-sets/<int:pk>/", rest_views.CouponSetsDetail.as_view(), name="coupon_sets_details"),
    path("coupon-sets/<int:pk>/usable/", rest_views.coupon_sets_usable, name="coupon_sets_usable"),
]
