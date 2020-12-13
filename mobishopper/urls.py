"""URLs for mobishopper."""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

# from django.contrib import admin

urlpatterns = [
    path("management/products/", include("ms_products.urls")),
    path("management/deals/", include("ms_deals.urls")),
    path("management/maps/", include("ms_maps.urls")),
    path("mangement/stats/", include("ms_userdata.urls")),
    path("", include("ms_baseline.urls_public")),
    path("api/", include("ms_baseline.urls_api")),
    path("management/", include("ms_baseline.urls_management")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path("api/products/", include("ms_products.urls_api")),
    path("api/deals/", include("ms_deals.urls_api")),
    path("api/maps/", include("ms_maps.urls_api")),
    path("api/lists/", include("ms_userdata.urls_lists_api")),
    path("api/checkout/", include("ms_userdata.urls_checkout_api")),
    path("lists/", include("ms_userdata.urls_share")),
    # The admin site is not used in production. Add from django.contrib import admin and uncomment below to use it.
    # path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
