"""General models used for Vue frontend."""
import datetime
import json
import typing

import attr
from django.urls import reverse
from django.utils.safestring import SafeString, mark_safe

import ms_baseline.models
import ms_products.models


def date_to_string_converter(dt: typing.Union[datetime.datetime, str]) -> str:
    """Convert a date to string (if it isn’t already a string)."""
    if isinstance(dt, datetime.datetime):
        return dt.isoformat()


def date_to_string_opt_converter(dt: typing.Union[None, datetime.datetime, str]) -> typing.Optional[str]:
    """Convert a date to string or None (if it isn’t already a string or None)."""
    if isinstance(dt, datetime.datetime):
        return dt.isoformat()


def enum_get_value(e):
    """Get value from an enum."""
    return e.value


# Models used in communication with Vue app
@attr.s(auto_attribs=True, slots=True, kw_only=True)
class LocalPermissionEntry:
    """A representation of a users’ local permissions."""

    id: int
    name: str
    can_manage_products: bool
    can_manage_maps: bool
    can_manage_deals: bool
    can_manage_employees: bool
    can_view_statistics: bool

    @classmethod
    def from_db(cls, usp: "ms_baseline.models.UserStorePermission") -> "LocalPermissionEntry":
        """Create a LocalPermissionEntry based on a UserStorePermission."""
        return LocalPermissionEntry(
            id=usp.store.id,
            name=usp.store.name,
            can_manage_products=usp.can_manage_products,
            can_manage_maps=usp.can_manage_maps,
            can_manage_deals=usp.can_manage_deals,
            can_manage_employees=usp.can_manage_employees,
            can_view_statistics=usp.can_view_statistics,
        )


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class ModalItem:
    """A modal item for the Modal Item Selector app."""

    id: int
    name: str
    details_url: str
    photo: typing.Optional[str] = None
    extras: typing.List[str] = attr.ib(factory=list)


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class ModalItemContainer:
    """A list of modal items."""

    items: typing.List[ModalItem]
    page: int
    num_pages: int


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class StandardMetaField:
    """A standard meta field."""

    slug: str
    name: str
    expected_units: str
    expected_units_names: typing.List[str]
    is_required: bool
    is_recommended: bool

    @classmethod
    def from_db(cls, s: "ms_products.models.StandardMetaField", subcategory=None):
        """Create a Vue StandardMetaField based on the database StandardMetaField."""
        if subcategory is None:
            is_required = is_recommended = False
        else:
            is_required = s.subcategories_required.filter(id=subcategory).exists()
            is_recommended = s.subcategories_recommended.filter(id=subcategory).exists()
        return cls(
            slug=s.slug,
            name=s.name,
            expected_units=s.expected_units,
            expected_units_names=s.expected_units_names,
            is_required=is_required,
            is_recommended=is_recommended,
        )


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class StandardMetaFieldContainer:
    """A standard meta field container."""

    items: typing.List[StandardMetaField]
    subcategory: typing.Optional[int]


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class MetaValue:
    """A meta value."""

    slug: typing.Optional[str]
    name: str
    value: str
    units: str
    text: str


# App data models


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class AppData:
    """Base class for Vue app data."""

    THIS_APP: str
    APP_TAG: str  # Must start with hash


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class AppDataLPT(AppData):
    """Vue app data for the Local Permissions Table app."""

    THIS_APP: str = attr.ib("users-edit-local-permissions", init=False)
    lpTableTitles: list
    lpEntries: list


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class AppDataMIS(AppData):
    """Vue app data for the Modal Item Selector app."""

    THIS_APP: str = attr.ib("modal-item-selector", init=False)
    misApiEndpoint: str
    misTitle: str
    misItemName: str
    misModalId: str
    misInputName: str
    misRequired: bool
    misExtraFieldNames: typing.List[str] = attr.ib(factory=list)
    misMultipleSelection: bool = False
    misInitialSelection: typing.List[ModalItem] = attr.ib(factory=list)


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class AppDataEME(AppData):
    """Vue app data for the Extra Metadata Editor app."""

    THIS_APP: str = attr.ib("extra-metadata-editor", init=False)
    emeApiEndpoint: str = attr.ib(factory=lambda: reverse("ms_products_api:standard_meta_fields"))
    emeUseSubcategory: bool = True
    emeHighlightCustom: bool = True
    emeInitialData: typing.List[MetaValue] = attr.ib(factory=list)


from ms_maps.api_models import AisleStructureEntry, MapDTO, MapTileDTO, ProductLocationFilter
from ms_products.api_models import CategoryStructureEntry


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class AppDataPLT(AppData):
    """Vue app data for the Product Locations Table app."""

    THIS_APP: str = attr.ib("product-locations-table", init=False)
    getEndpoint: str = attr.ib(factory=lambda: reverse("ms_maps_api:product_locations"))
    groupsEndpoint: str = attr.ib(factory=lambda: reverse("ms_maps_api:product_locations_groups"))
    updateEndpoint: str = attr.ib(factory=lambda: reverse("ms_maps_api:product_locations"))
    defaultPageSize: int
    initialView: typing.Union[str, ProductLocationFilter] = attr.ib(converter=enum_get_value)
    categoryStructure: typing.List[CategoryStructureEntry]


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class AppDataMSD(AppData):
    """Vue app data for the Map Static Display app."""

    THIS_APP: str = attr.ib("map-static-display", init=False)
    map: MapDTO
    tiles: typing.List[MapTileDTO]
    aisles: typing.List[AisleStructureEntry]


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class AppDataSME(AppData):
    """Vue app data for the Store Map Editor app."""

    THIS_APP: str = attr.ib("map-editor", init=False)
    map: typing.Optional[MapDTO]
    defaultSize: int
    tiles: typing.List[MapTileDTO]
    aisles: typing.List[AisleStructureEntry]
    aislesEndpoint: str = attr.ib(factory=lambda: reverse("ms_maps_api:aisles_structure"))
    saveEndpoint: str = attr.ib(factory=lambda: reverse("ms_maps_api:maps_save"))


def get_json(vue_apps: typing.List[AppData]) -> SafeString:
    """Get the Vue apps list as JSON."""
    vue_apps_dicts = [attr.asdict(app) for app in vue_apps]
    return mark_safe(json.dumps(vue_apps_dicts))
