"""URL configuration for ms_products."""
from django.urls import path

import ms_products.views.product_management as views_products
import ms_products.views.product_organization as views_organization

app_name = "ms_products"
urlpatterns = [
    path("", views_products.products_overview, name="products_overview"),
    path("<int:id>/", views_products.products_show_edit, name="show_edit"),
    path("search/", views_products.products_search, name="search"),
    path("list/", views_products.products_list, name="list"),
    path("recent-upcoming/", views_products.products_recent_upcoming, name="recent_upcoming"),
    path("add/", views_products.products_add, name="add"),
    path("categories/", views_organization.categories_list, name="categories"),
    path("categories/add/", views_organization.categories_add, name="categories_add"),
    path("categories/<int:id>/", views_organization.categories_search, name="categories_search"),
    path("categories/<int:id>/edit/", views_organization.categories_edit, name="categories_edit"),
    path("subcategories/<int:id>/", views_organization.subcategories_search, name="subcategories_search"),
    path("subcategories/<int:id>/edit/", views_organization.subcategories_edit, name="subcategories_edit"),
    path("subcategories/add/", views_organization.subcategories_add, name="subcategories_add"),
    path("global-subaisles/", views_organization.global_subaisles_list, name="global_subaisles"),
    path("global-subaisles/add/", views_organization.global_subaisles_add, name="global_subaisles_add"),
    path("global-subaisles/<int:id>/", views_organization.global_subaisles_edit, name="global_subaisles_edit"),
    path(
        "global-subaisles/<int:id>/delete/", views_organization.global_subaisles_delete, name="global_subaisles_delete"
    ),
    path("groups/", views_organization.groups_list, name="groups"),
    path("groups/search/", views_organization.groups_search, name="groups_search"),
    path("groups/add/", views_organization.groups_add, name="groups_add"),
    path("groups/<int:id>/", views_organization.groups_show, name="groups_show"),
    path("groups/<int:id>/edit/", views_organization.groups_edit, name="groups_edit"),
    path("groups/<int:id>/delete/", views_organization.groups_delete, name="groups_delete"),
    path("vendors/", views_organization.vendors_list, name="vendors"),
    path("vendors/add/", views_organization.vendors_add, name="vendors_add"),
    path("vendors/<int:id>/", views_organization.vendors_show, name="vendors_show"),
    path("vendors/<int:id>/edit/", views_organization.vendors_edit, name="vendors_edit"),
    path("properties/", views_organization.properties_list, name="properties"),
    path("properties/add/", views_organization.properties_add, name="properties_add"),
    path("properties/<int:id>/edit/", views_organization.properties_edit, name="properties_edit"),
    path("properties/<int:id>/delete/", views_organization.properties_delete, name="properties_delete"),
    path("local-overrides/", views_products.products_local_overrides, name="local_overrides"),
]
