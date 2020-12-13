"""URL configuration for ms_products (API)."""
from django.urls import path

from ms_products.views import api_views, rest_views

app_name = "ms_products_api"
urlpatterns = [
    path("standard-meta-fields/", api_views.get_standard_meta_fields, name="standard_meta_fields"),
    path(
        "standard-meta-fields/<int:subcategory>/",
        api_views.get_standard_meta_fields,
        name="standard_meta_fields_subcategory",
    ),
    path("products-modal/", api_views.list_products_modal, name="products_modal"),
    path("vendors-modal/", api_views.list_vendors_modal, name="vendors_modal"),
    path("groups-modal/", api_views.list_groups_modal, name="groups_modal"),
    path("", rest_views.ProductsList.as_view(), name="products"),
    path("<int:pk>/", rest_views.ProductsDetail.as_view(), name="products_details"),
    path("categories/", api_views.categories_structure, name="categories_structure"),
    path("subcategories/", rest_views.SubcategoriesList.as_view(), name="subcategories_list"),
    path("vendors/", rest_views.VendorsList.as_view(), name="vendors_list"),
    path("vendors/<int:pk>/", rest_views.VendorsDetail.as_view(), name="vendors_details"),
    path("vendors/<int:pk>/products/", rest_views.VendorsProductsList.as_view(), name="vendors_products_list"),
    path("groups/", rest_views.ProductGroupsList.as_view(), name="productgroups_list"),
    path("groups/<int:pk>/", rest_views.ProductGroupsDetail.as_view(), name="productgroups_details"),
    path("bulk/", rest_views.bulk_find_products, name="bulk_find_products"),
]
