"""URLs for ms_baseline (API module)."""

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from ms_baseline.views import api_views

app_name = "ms_baseline_api"
urlpatterns = [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", api_views.register, name="register"),
    path("profile/", api_views.profile, name="profile"),
    path("stores/", api_views.list_stores, name="api_list_stores"),
    path("stores/default/", api_views.set_default_store, name="api_default_store"),
    path("whoami/", api_views.whoami, name="api_whoami"),
]
