"""URL configuration for ms_maps (API)."""

from django.urls import path

from ms_maps.views import api_views

app_name = "ms_maps_api"
urlpatterns = [
    path("", api_views.get_map, name="get_map"),
    path("aisles/", api_views.aisles_structure, name="aisles_structure"),
    path("ajax/aisles/add/", api_views.ajax_aisles_add, name="aisles_add"),
    path("ajax/aisles/<int:id>/", api_views.ajax_aisles_edit, name="aisles_edit"),
    path("ajax/subaisles/add/", api_views.ajax_subaisles_add, name="subaisles_add"),
    path("ajax/subaisles/<int:id>/", api_views.ajax_subaisles_edit, name="subaisles_edit"),
    path("locations/", api_views.ProductLocationsBulk.as_view(), name="product_locations_bulk"),
    path("locations/<int:product_id>/", api_views.ProductLocationsDetail.as_view(), name="product_locations_product"),
    path("current/", api_views.MapsCurrent.as_view(), name="maps_current"),
    path("m/locations/", api_views.product_locations, name="product_locations"),
    path("m/locations/groups/", api_views.product_locations_groups, name="product_locations_groups"),
    path("m/edit/", api_views.maps_save, name="maps_save"),
]
