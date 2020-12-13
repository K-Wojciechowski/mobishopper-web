"""URLs for ms_baseline (management module)."""
from django.urls import path

import ms_baseline.views.store_management as store_management_views
import ms_baseline.views.user_management as user_management_views
from ms_baseline import views

app_name = "ms_baseline"
urlpatterns = [
    path("", views.management_home, name="management_home"),
    path("change-store/<int:sid>/", views.change_store, name="change_store"),
    path("my-permissions/", views.my_permissions, name="my_permissions"),
    path("users/", user_management_views.users_list, name="users_list"),
    path("users/add/", user_management_views.users_add, name="users_add"),
    path("users/<int:id>/", user_management_views.users_edit, name="users_edit"),
    path(
        "users/<int:id>/reset-password/",
        user_management_views.users_reset_password,
        name="users_reset_password",
    ),
    path("users/<int:id>/delete/", user_management_views.users_delete, name="users_delete"),
    path("users/change-type/", user_management_views.users_change_type, name="users_change_type"),
    path("stores/", store_management_views.stores_list, name="stores_list"),
    path("stores/add/", store_management_views.stores_add, name="stores_add"),
    path("stores/<int:id>/", store_management_views.stores_edit, name="stores_edit"),
    path("stores/<int:id>/users/", store_management_views.stores_users, name="stores_users"),
    path("stores/<int:id>/delete/", store_management_views.stores_delete, name="stores_delete"),
    path("checkout-api-keys/", store_management_views.checkout_api_keys_list, name="checkout_api_keys_list"),
    path("checkout-api-keys/add/", store_management_views.checkout_api_keys_add, name="checkout_api_keys_add"),
    path("checkout-api-keys/<int:id>/", store_management_views.checkout_api_keys_edit, name="checkout_api_keys_edit"),
    path(
        "checkout-api-keys/<int:id>/delete/",
        store_management_views.checkout_api_keys_delete,
        name="checkout_api_keys_delete",
    ),
]
