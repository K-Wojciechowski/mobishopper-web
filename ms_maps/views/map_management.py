"""Map management views for ms_maps."""

import django.utils.timezone
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from ms_baseline import constants, vue_models
from ms_baseline.permission_helpers import permissions_required_maps
from ms_baseline.utils import filter_in_effect_this_store, filter_this_store, paginate, render
from ms_maps import auto_assign, forms
from ms_maps.api_models import MapDTO, MapTileDTO, ProductLocationFilter, build_vue_aisles_structure
from ms_maps.models import Aisle, Map, ProductLocation, Subaisle
from ms_maps.utils import get_map_in_effect, get_missing_product_locations
from ms_products.api_models import build_vue_categories_structure
from ms_products.models import GenericSubaisle


@permissions_required_maps
def maps_overview(request):
    """Show an overview of map-related data."""
    now = django.utils.timezone.now()
    missing = get_missing_product_locations(request.ms_store)
    context = {
        "map_in_effect": get_map_in_effect(request, now),
        "aisles": Aisle.objects.filter(filter_this_store(request), visible=True).count(),
        "subaisles": Subaisle.objects.filter(filter_this_store(request), visible=True).count(),
        "global_aisles": GenericSubaisle.objects.filter().count(),
        "human": ProductLocation.objects.filter(filter_in_effect_this_store(request, now), is_auto=False).count(),
        "auto": ProductLocation.objects.filter(filter_in_effect_this_store(request, now), is_auto=True).count(),
        "missing": missing.count(),
    }

    return render(request, "mobishopper/maps/maps_overview.html", _("Maps overview"), context)


@permissions_required_maps
def product_locations(request):
    """Show a list of product locations."""
    initial_filter_str = request.GET.get("filter", "missing")
    try:
        initial_filter = ProductLocationFilter(initial_filter_str)
    except ValueError:
        initial_filter = ProductLocationFilter.ALL

    context = {
        "vue_apps_json": vue_models.get_json(
            [
                vue_models.AppDataPLT(
                    APP_TAG="#product-locations",
                    defaultPageSize=settings.MOBISHOPPER_PAGE_SIZE,
                    initialView=initial_filter,
                    categoryStructure=build_vue_categories_structure(),
                )
            ]
        ),
        "datepicker_form": forms.DatePickerPlaceholderForm(),
    }
    return render(request, "mobishopper/maps/products_locations.html", _("Product locations"), context)


@permissions_required_maps
def product_locations_auto(request):
    """Automatically assign product locations."""
    if request.method == "GET":
        context = {"missing": get_missing_product_locations(request.ms_store).count()}
        return render(
            request, "mobishopper/maps/products_locations_auto_get.html", _("Auto-assign product locations"), context
        )
    else:
        log = auto_assign.AutoAssignHtmlLogWriter()
        auto_assign.auto_assign(log, stores=[request.ms_store])
        context = {"missing": get_missing_product_locations(request.ms_store).count(), "assign_log": log.get()}
        return render(
            request, "mobishopper/maps/products_locations_auto_results.html", _("Auto-assignment complete"), context
        )


@permissions_required_maps
def maps_show_current(request):
    """Show the current map."""
    map_in_effect = get_map_in_effect(request)
    if map_in_effect:
        return redirect(map_in_effect.get_absolute_url())
    return render(request, "mobishopper/maps/maps_no_current.html", _("No current map"), {})


@permissions_required_maps
def maps_edit_current(request):
    """Edit the current map."""
    map_in_effect = get_map_in_effect(request)
    if map_in_effect:
        return redirect(reverse("ms_maps:maps_edit", args=(map_in_effect.id,)))
    return render(request, "mobishopper/maps/maps_no_current.html", _("No current map"), {})


@permissions_required_maps
def maps_show(request, id):
    """Show a map."""
    store_map = get_object_or_404(Map, id=id)
    map_dto = MapDTO.from_db(store_map)
    tiles = [MapTileDTO.from_db(t) for t in store_map.tiles.all()]
    aisles = build_vue_aisles_structure(request.ms_store)
    vue_apps_json = vue_models.get_json(
        [vue_models.AppDataMSD(APP_TAG="#map-show-edit", map=map_dto, tiles=tiles, aisles=aisles)]
    )
    return render(request, "mobishopper/maps/maps_show.html", str(store_map), {"vue_apps_json": vue_apps_json})


@permissions_required_maps
def maps_edit(request, id):
    """Edit a map."""
    store_map = get_object_or_404(Map, id=id)
    map_dto = MapDTO.from_db(store_map)
    tiles = [MapTileDTO.from_db(t) for t in store_map.tiles.all()]
    aisles = build_vue_aisles_structure(request.ms_store)
    not_latest = store_map.date_ended is not None
    vue_apps_json = vue_models.get_json(
        [
            vue_models.AppDataSME(
                APP_TAG="#map-show-edit",
                map=map_dto,
                defaultSize=constants.DEFAULT_MAP_SIZE,
                tiles=tiles,
                aisles=aisles,
            )
        ]
    )
    return render(
        request,
        "mobishopper/maps/maps_edit.html",
        _("Edit map"),
        {
            "vue_apps_json": vue_apps_json,
            "datepicker_form": forms.DatePickerPlaceholderForm(),
            "not_latest": not_latest,
        },
    )


@permissions_required_maps
def maps_list(request):
    """List maps."""
    maps = Map.objects.filter(filter_this_store(request)).order_by("-date_started")

    paginator, page = paginate(maps, request)

    return render(request, "mobishopper/maps/maps_list.html", _("Map history"), {"maps": page, "paginator": paginator})


@permissions_required_maps
def maps_new(request):
    """Create a new map."""
    has_existing = Map.objects.filter(filter_this_store(request)).count() > 0
    aisles = build_vue_aisles_structure(request.ms_store)
    vue_apps_json = vue_models.get_json(
        [
            vue_models.AppDataSME(
                APP_TAG="#map-show-edit", map=None, defaultSize=constants.DEFAULT_MAP_SIZE, tiles=[], aisles=aisles
            )
        ]
    )
    return render(
        request,
        "mobishopper/maps/maps_edit.html",
        _("Create new map"),
        {
            "vue_apps_json": vue_apps_json,
            "datepicker_form": forms.DatePickerPlaceholderForm(),
            "new_has_existing": has_existing,
        },
    )
