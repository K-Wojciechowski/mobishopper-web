"""URL configuration for ms_userdata."""

from django.urls import path

from ms_userdata import views

app_name = "ms_userdata"
urlpatterns = [
    path("", views.stats_overview, name="stats_overview"),
    path("coupons/", views.popular_coupons, name="popular_coupons"),
    path("products/", views.popular_products, name="popular_products"),
]
