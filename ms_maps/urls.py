"""URL configuration for ms_maps."""

from django.urls import path

from ms_maps.views import aisle_management as aisle_views
from ms_maps.views import map_management as map_views

app_name = "ms_maps"
urlpatterns = [
    path("", map_views.maps_overview, name="maps_overview"),
    path("current/", map_views.maps_show_current, name="maps_show_current"),
    path("current/edit/", map_views.maps_edit_current, name="maps_edit_current"),
    path("new/", map_views.maps_new, name="maps_new"),
    path("list/", map_views.maps_list, name="maps_list"),
    path("<int:id>/", map_views.maps_show, name="maps_show"),
    path("<int:id>/edit/", map_views.maps_edit, name="maps_edit"),
    path("products/", map_views.product_locations, name="product_locations"),
    path("products/auto/", map_views.product_locations_auto, name="product_locations_auto"),
    path("aisles/", aisle_views.aisles_list, name="aisles_list"),
    path("aisles/add/", aisle_views.aisles_add, name="aisles_add"),
    path("aisles/<int:id>/", aisle_views.aisles_edit, name="aisles_edit"),
    path("aisles/<int:id>/delete/", aisle_views.aisles_delete, name="aisles_delete"),
    path("subaisles/add/", aisle_views.subaisles_add, name="subaisles_add"),
    path("subaisles/<int:id>/", aisle_views.subaisles_edit, name="subaisles_edit"),
    path("subaisles/<int:id>/delete/", aisle_views.subaisles_delete, name="subaisles_delete"),
]
