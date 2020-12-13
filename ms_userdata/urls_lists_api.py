"""URL configuration for ms_userdata (API views)."""

from django.urls import path

from ms_userdata.views import rest_views

app_name = "ms_userdata_api"
urlpatterns = [
    path("", rest_views.ShoppingListsList.as_view(), name="lists_list"),
    path("<int:pk>/", rest_views.ShoppingListDetail.as_view(), name="lists_detail"),
    path("<int:pk>/product/<int:product_pk>/", rest_views.shopping_list_entry, name="lists_entry"),
    path("<int:pk>/share/", rest_views.shopping_list_share, name="lists_share"),
    path("<int:pk>/clean/", rest_views.shopping_list_clean_done_items, name="lists_clean_done_items"),
    path("<int:list_pk>/invites/", rest_views.ShoppingListInviteList.as_view(), name="lists_invites_list"),
    path(
        "<int:list_pk>/invites/<uuid:pk>/", rest_views.ShoppingListInviteDetail.as_view(), name="lists_invites_detail"
    ),
    path("<int:pk>/members/", rest_views.get_delete_list_members, name="lists_members"),
    path("<int:pk>/members/<int:user_pk>/", rest_views.remove_list_member, name="lists_members_remove"),
    path("invites/<uuid:uuid>/", rest_views.invite_details_accept, name="lists_invite_details_accept"),
]
