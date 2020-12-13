"""URL configuration for ms_userdata (Checkout API views)."""

from django.urls import path

from ms_userdata.views import checkout_api_views

app_name = "ms_userdata_checkout_api"
urlpatterns = [
    path("coupon/", checkout_api_views.checkout_coupon, name="checkout_coupon"),
]
