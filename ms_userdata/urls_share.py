"""URL configuration for ms_userdata."""

from django.urls import path

from ms_userdata import views

app_name = "ms_userdata_share"
urlpatterns = [
    path("shared/<uuid:uuid>/", views.shared_list, name="shared_list"),
    path("invite/<uuid:uuid>/", views.accept_invite, name="accept_invite"),
]
