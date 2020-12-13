"""URLs for ms_baseline (public module)."""

from django.urls import path

from ms_baseline import views

app_name = "ms_baseline_public"
urlpatterns = [
    path("", views.landing_page, name="landing_page"),
]
