"""API views for ms_maps."""
import datetime
import json
import logging
import typing

import attr
import cattr
import django.utils.dateparse
import django.utils.timezone
import rest_framework.exceptions
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from django.utils.translation import ngettext
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response

import ms_products.api_models
from ms_baseline.api_utils import asdict_json_response
from ms_baseline.permission_helpers import permissions_required_maps
from ms_baseline.serializers import SerializerContextMixin
from ms_baseline.utils import (
    filter_in_effect,
    filter_in_effect_after,
    filter_in_effect_resolved_store,
    filter_in_effect_this_store,
    filter_resolved_store,
    filter_this_store,
    get_resolved_store,
    render,
)
from ms_maps import api_models, forms, models
from ms_maps.models import Aisle, Map, MapTile, ProductLocation, Subaisle
from ms_maps.serializers import MapSerializer, ProductLocationSerializer
from ms_maps.utils import get_map_in_effect
from ms_maps.views.aisle_dual_forms import FormType, GenericFormStatus, InstanceType, generic_add, generic_edit
from ms_products.models import Product

logger = logging.getLogger("ms_maps.api_views")


class MapsCurrent(SerializerContextMixin, generics.RetrieveAPIView):
    """Get the current map for the user’s store."""

    serializer_class = MapSerializer

    def get_object(self):
        """Get the current map for a store."""
        map_in_effect = get_map_in_effect(self.request)
        if not map_in_effect:
            raise rest_framework.exceptions.NotFound()
        return map_in_effect


class ProductLocationsDetail(SerializerContextMixin, generics.RetrieveAPIView):
    """Get one product location."""

    lookup_field = "product_id"
    serializer_class = ProductLocationSerializer

    def get_object(self):
        """Get a product location."""
        return get_object_or_404(
            ProductLocation.objects.select_related("product", "tile", "subaisle"),
            filter_resolved_store(self.request),
            product=self.kwargs["product_id"],
        )


class ProductLocationsBulk(SerializerContextMixin, generics.ListAPIView):
    """Get locations of multiple products."""

    serializer_class = ProductLocationSerializer
    pagination_class = None

    def get_queryset(self):
        """Get the queryset for a product location list."""
        return ProductLocation.objects.filter(
            filter_in_effect_resolved_store(self.request), product__in=self.request.query_params.getlist("product")
        ).order_by("product__name")


def show_generic_form(
    request, status: GenericFormStatus, form: FormType, form_name: str, extras: typing.Dict[str, typing.Any]
):
    """Show a generic AJAX form."""
    if status == GenericFormStatus.success:
        return HttpResponse(_("Changes saved.").encode("utf-8"), status=201)

    context = {"form": form, "form_name": form_name}
    context.update(extras)

    status_code = 200 if status.show_form else 400
    return render(request, "mobishopper/maps/ajax_aisle_form_holder.html", "", context, status=status_code)


def show_add_form(request, form_cls: typing.Type[FormType], form_name: str):
    """Show an addition form."""
    status, form, _, extras = generic_add(request, form_cls, show_success_message=False)
    return show_generic_form(request, status, form, form_name, extras)


def show_edit_form(request, instance: InstanceType, form_cls: typing.Type[FormType], form_name: str):
    """Show an edit form."""
    status, form, _, extras = generic_edit(request, instance, form_cls, show_success_message=False)
    return show_generic_form(request, status, form, form_name, extras)


@permissions_required_maps
def ajax_aisles_add(request):
    """Add an aisle (AJAX form)."""
    return show_add_form(request, forms.AisleAddEditForm, "aisle")


@permissions_required_maps
def ajax_aisles_edit(request, id):
    """Edit an aisle (AJAX form)."""
    instance = get_object_or_404(Aisle, id=id)
    return show_edit_form(request, instance, forms.AisleAddEditForm, "aisle")


@permissions_required_maps
def ajax_subaisles_add(request):
    """Add a subaisle (AJAX form)."""
    return show_add_form(request, forms.SubaisleAddEditForm, "subaisle")


@permissions_required_maps
def ajax_subaisles_edit(request, id):
    """Edit a subaisle (AJAX form)."""
    instance = get_object_or_404(Subaisle, id=id)
    return show_edit_form(request, instance, forms.SubaisleAddEditForm, "subaisle")


@permissions_required_maps
def product_locations(request):
    """Get or update of product locations."""
    if request.method == "GET":
        return _get_product_locations(request)
    elif request.method == "POST":
        return _post_product_locations(request)
    return HttpResponseBadRequest()


def _get_product_locations(request):
    """Get a list of product locations."""
    valid_at = request.GET.get("valid_at", django.utils.timezone.now())
    filter_str = request.GET.get("filter", "all")
    subcategory = request.GET.get("subcategory")
    vendor = request.GET.get("vendor")
    query = request.GET.get("q")
    page_number = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", settings.MOBISHOPPER_PAGE_SIZE)

    try:
        loc_filter = api_models.ProductLocationFilter(filter_str)
    except ValueError:
        loc_filter = api_models.ProductLocationFilter.ALL

    return _get_product_locations_data(
        request, valid_at, subcategory, vendor, query, page_number, page_size, loc_filter
    )


def _get_product_locations_data(
    request,
    valid_at: typing.Union[str, datetime.datetime],
    subcategory: typing.Union[str, int, None],
    vendor: typing.Optional[str],
    query: typing.Optional[str],
    page_number: int,
    page_size: int,
    loc_filter: api_models.ProductLocationFilter,
) -> JsonResponse:
    """Get product locations data."""
    filters_list = [filter_in_effect_this_store(request, valid_at)]
    filters_dict = {}

    if query and query.strip():
        filters_dict["name__icontains"] = query.strip()

    if vendor and vendor.strip():
        filters_dict["vendor__name__icontains"] = vendor.strip()

    if subcategory:
        try:
            filters_dict["subcategory"] = int(subcategory)
        except ValueError:
            pass

    if loc_filter == api_models.ProductLocationFilter.AUTO:
        filters_dict["productlocation__is_auto"] = True
    elif loc_filter == api_models.ProductLocationFilter.MANUAL:
        filters_dict["productlocation__is_auto"] = False

    if loc_filter in (api_models.ProductLocationFilter.AUTO, api_models.ProductLocationFilter.MANUAL):
        filters_list.append(filter_in_effect_this_store(request, prefix="productlocation__"))
    elif loc_filter == api_models.ProductLocationFilter.MISSING:
        filters_list.append(~filter_in_effect_this_store(request, prefix="productlocation__"))

    queryset = (
        Product.objects.filter(*filters_list, **filters_dict).order_by("name").select_related("vendor", "subcategory")
    )

    if not queryset and loc_filter == api_models.ProductLocationFilter.MISSING:
        # If there is no missing data, get all locations as a fallback. The view defaults to MISSING,
        # but it can switch to ALL if there are no products with missing locaitons.
        # Doing this at the backend level avoids another round-trip.
        return _get_product_locations_data(
            request, valid_at, subcategory, vendor, query, page_number, page_size, api_models.ProductLocationFilter.ALL
        )

    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_number)

    output_objects: typing.List[api_models.ProductToLocate] = []
    for product in page.object_list:
        locations = product.productlocation_set.filter(filter_in_effect_this_store(request)).select_related(
            "tile", "subaisle"
        )
        location = None if not locations else locations[0]

        if len(locations) > 1:
            logger.error(
                f"Found multiple location objects for product {product} in store {request.ms_store} at {valid_at}."
            )

        output_objects.append(api_models.ProductToLocate.from_db(product, location))

    response = api_models.ProductLocationGetResponse(
        products=output_objects, page=page.number, totalPages=paginator.num_pages, filter=loc_filter
    )

    return asdict_json_response(response)


def _parse_datetime_tz(date: str) -> datetime.datetime:
    """Parse a datetime and ensure it’s timezone-aware."""
    dt = django.utils.dateparse.parse_datetime(date)
    if not dt.tzinfo:
        # Ensure the datetime is tz-aware.
        current_tz = django.utils.timezone.get_current_timezone()
        dt = current_tz.localize(dt)
    return dt


def _post_product_locations(request):
    """Save changes to product locations."""
    # Deserialize data from POST request
    json_data: dict = json.loads(request.body.decode("utf-8"))
    data: api_models.ProductLocationChangeDescription = cattr.structure(
        json_data, api_models.ProductLocationChangeDescription
    )
    date_started: datetime.datetime = _parse_datetime_tz(data.date)

    failed_auto = []

    for change in data.changes:
        existing_locations = ProductLocation.objects.filter(
            filter_in_effect(date_started), product=change.product.id, store=request.ms_store
        )
        for existing_location in existing_locations:
            existing_location.date_ended = date_started
            existing_location.save()
        if change.delete_location:
            continue

        new_location = ProductLocation(
            product_id=change.product.id, date_started=date_started, store=request.ms_store, user=request.user
        )
        if change.revert_auto:
            created_auto = new_location.compute_auto_location(date_started)
            if created_auto:
                new_location.save()
            else:
                failed_auto.append(change.product.name)
        else:
            if change.subaisle:
                new_location.subaisle_id = change.subaisle.id
            if change.tile:
                new_location.tile_id = change.tile.id
            new_location.save()

    failed_locations = len(failed_auto)
    success_locations = len(data.changes) - failed_locations
    success_msg = ngettext(
        "Changes saved to {0} location.", "Changes saved to {0} locations.", success_locations
    ).format(success_locations)
    failed_msg = ngettext(
        "Could not compute the location of {0} product automatically, no changes were made to it.",
        "Could not compute the locations of {0} products automatically, no changes were made to them.",
        failed_locations,
    ).format(failed_locations)
    if failed_auto:
        out = api_models.ProductLocationChangeResponse(
            success=False, message=success_msg + " " + failed_msg, warning=True
        )
        status = 500
    else:
        out = api_models.ProductLocationChangeResponse(success=True, message=success_msg)
        status = 200

    return asdict_json_response(out, status)


@permissions_required_maps
def product_locations_groups(request):
    """Get a list of groups for product locations."""
    valid_at = request.GET.get("valid_at", django.utils.timezone.now())
    try:
        store_map = Map.objects.get(filter_in_effect(valid_at), store=request.ms_store)
    except Map.DoesNotExist:
        store_map = None
    if store_map:
        map_dto = api_models.MapDTO.from_db(store_map)
        map_tiles = MapTile.objects.filter(map=store_map)
    else:
        map_dto = None
        map_tiles = []

    db_subaisles = Subaisle.objects.filter(visible=True, store=request.ms_store).select_related("parent")
    groups = api_models.ProductGroupsGetResponse(
        map=map_dto,
        tiles=[api_models.MapTileDTO.from_db(t) for t in map_tiles],
        categoryStructure=ms_products.api_models.build_vue_categories_structure(),
        aisleStructure=api_models.build_vue_aisles_structure(request.ms_store),
        subaisles=[api_models.Subaisle.from_db(s) for s in db_subaisles],
    )
    return asdict_json_response(groups)


@api_view()
def aisles_structure(request):
    """Get the aisles structure."""
    store = get_resolved_store(request)
    if store is None:
        aisles = []
    else:
        aisles = api_models.build_vue_aisles_structure(store)
    return Response([attr.asdict(a) for a in aisles])


@api_view()
def get_map(request):
    """Get the map for a given store."""
    store = get_resolved_store(request)
    if store is None:
        return Response({"error": _("No store provided")}, 400)

    try:
        store_map = Map.objects.get(filter_in_effect(), store=store)
    except Map.DoesNotExist:
        return Response({"error": _("Not found")}, 404)
    map_dto = api_models.MapDTO.from_db(store_map)
    tiles_dtos = [api_models.MapTileDTO.from_db(t) for t in store_map.maptile_set.all()]
    return Response({"map": attr.asdict(map_dto), "tiles": [attr.asdict(t) for t in tiles_dtos]})


def _messages_as_map_save_error(request):
    """Return messages as a map save error."""
    messages_string = "\n".join(str(m) for m in messages.get_messages(request))
    if not messages_string:
        messages_string = _("Failed to save changes!")
    return asdict_json_response(api_models.MapSaveResponse(success=False, message=messages_string), status=500)


@permissions_required_maps
def maps_save(request):
    """Save changes to a map."""
    if request.ms_store is None:
        return asdict_json_response(
            api_models.MapSaveResponse(success=False, message=_("You can only edit maps in a store context.")),
            status=401,
        )

    json_data: dict = json.loads(request.body.decode("utf-8"))
    data: api_models.MapSaveRequest = cattr.structure(json_data, api_models.MapSaveRequest)
    date_started: datetime.datetime = _parse_datetime_tz(data.date)

    # Prepare map.
    store_map = models.Map(
        width=data.map.width,
        height=data.map.height,
        user=request.user,
        store=request.ms_store,
        date_started=date_started,
    )

    # Prepare tiles.
    tiles = []
    tile_replacements: typing.Dict[int, MapTile] = {}
    subaisles = {s.id: s for s in Subaisle.objects.filter(filter_this_store(request))}
    for tile_dto in data.tiles:
        subaisle = None
        if tile_dto.subaisle:
            subaisle = subaisles.get(tile_dto.subaisle.id)
        tile = models.MapTile(
            map=store_map,
            x=tile_dto.x,
            y=tile_dto.y,
            tile_type=tile_dto.tile_type,
            subaisle=subaisle,
            color=tile_dto.color,
            color_is_light=tile_dto.color_is_light,
        )
        tiles.append(tile)
        if tile_dto.id:
            tile_replacements[tile_dto.id] = tile

    old_map = None
    try:
        if data.map.id:
            old_map = Map.objects.get(id=data.map.id)
    except Map.DoesNotExist:
        pass

    try:
        with transaction.atomic():
            if old_map:
                success = store_map.save_as_replacement(request, old_map, quiet=True)
                if not success:
                    raise ValueError("Save failed")
            else:
                success = store_map.save_with_error_message(request)
                if not success:
                    raise ValueError("Save failed")

            for tile in tiles:
                tile.save()

    except Exception as e:
        logger.exception("Failed to save map")
        return _messages_as_map_save_error(request)

    # Ensure only one map is in effect.
    maps_in_effect = Map.objects.filter(
        filter_in_effect_this_store(request, date_started + datetime.timedelta(seconds=1))
    )
    for m in maps_in_effect:
        m: Map
        if m.id != store_map.id:
            m.date_ended = date_started
            success = m.save_with_error_message(request)
            if not success:
                return _messages_as_map_save_error(request)

    # Update ProductLocations with new tiles.
    locs = ProductLocation.objects.filter(
        filter_in_effect_after(), filter_this_store(request), tile__in=list(tile_replacements.keys())
    ).prefetch_related("tile")
    loc_all_success = True
    for loc in locs:
        loc: ProductLocation
        new_tile = None
        try:
            new_tile = tile_replacements[loc.tile.id]
            change_tile = new_tile.tile_type == loc.tile.tile_type and new_tile.subaisle_id == loc.tile.subaisle_id
        except ValueError:
            change_tile = False

        if change_tile:
            # Create a new replacement location.
            old_id: int = loc.id
            loc.id = None
            loc.pk = None
            loc.date_started = date_started
            loc.tile = new_tile
            old_loc: ProductLocation = ProductLocation.objects.get(id=old_id)
            loc_all_success = loc_all_success and loc.save_as_replacement(request, old_loc, quiet=True)
        else:
            # Update the validity of the location.
            loc.date_ended = date_started
            loc_all_success = loc_all_success and loc.save_with_error_message(request)

    map_dto = api_models.MapDTO.from_db(store_map)
    tiles_dto = [api_models.MapTileDTO.from_db(t) for t in store_map.tiles.all()]

    if not loc_all_success:
        return asdict_json_response(
            api_models.MapSaveResponse(
                success=True,
                warning=True,
                message=_(
                    "Map has been saved, but there was an error updating product locations to point to the new map."
                ),
                map=map_dto,
                tiles=tiles_dto,
            )
        )
    return asdict_json_response(
        api_models.MapSaveResponse(success=True, message=_("Changes saved."), map=map_dto, tiles=tiles_dto)
    )
