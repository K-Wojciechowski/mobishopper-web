"""Vue models for ms_maps."""
import datetime
import enum
import typing

import attr
import cattr

import ms_products.models
from ms_maps import models
from ms_maps.utils import build_aisles_structure
from ms_products.api_models import CategoryStructureEntry

cattr.register_structure_hook(typing.Union[str, datetime.datetime], lambda d, _t: d)
cattr.register_structure_hook(typing.Union[None, str, datetime.datetime], lambda d, _t: d)


class ProductLocationFilter(enum.Enum):
    """Filters for product locations."""

    ALL = "all"
    AUTO = "auto"
    MANUAL = "manual"
    MISSING = "missing"


from ms_baseline.vue_models import date_to_string_opt_converter, enum_get_value  # NOQA


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class Category:
    """A category in a API-friendly format."""

    id: int
    name: str
    description: str
    visible: bool

    @classmethod
    def from_db(cls, db_cat: ms_products.models.Category) -> "Category":
        """Convert a database Category to an API Category."""
        return cls(id=db_cat.id, name=db_cat.name, description=db_cat.description, visible=db_cat.visible)


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class Subcategory:
    """A subcategory in a API-friendly format."""

    id: int
    name: str
    description: str
    visible: bool
    parent: Category

    @classmethod
    def from_db(cls, db_sc: ms_products.models.Subcategory) -> "Subcategory":
        """Convert a database Subcategory to an API Subcategory."""
        return cls(
            id=db_sc.id,
            name=db_sc.name,
            description=db_sc.description,
            visible=db_sc.visible,
            parent=Category.from_db(db_sc.parent),
        )


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class Aisle:
    """An aisle in a API-friendly format."""

    id: int
    name: str
    code: str
    description: str
    visible: bool

    @classmethod
    def from_db(cls, db_aisle: models.Aisle) -> "Aisle":
        """Convert a database Aisle to an API Aisle."""
        return cls(
            id=db_aisle.id,
            name=db_aisle.name,
            code=db_aisle.name,
            description=db_aisle.description,
            visible=db_aisle.visible,
        )


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class Subaisle:
    """A subaisle in a API-friendly format."""

    id: int
    name: str
    code: str
    display_code: str
    description: str
    visible: bool
    parent: Aisle
    subcategories: typing.List[Subcategory] = attr.ib(factory=list)

    @classmethod
    def from_db(cls, db_sa: models.Subaisle) -> "Subaisle":
        """Convert a database Subaisle to an API Subaisle."""
        return cls(
            id=db_sa.id,
            name=db_sa.name,
            code=db_sa.code,
            display_code=db_sa.display_code,
            description=db_sa.description,
            visible=db_sa.visible,
            parent=Aisle.from_db(db_sa.parent),
            subcategories=[Subcategory.from_db(sc) for sc in db_sa.subcategories.filter(visible=True)],
        )


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class AisleStructureEntry:
    """An aisle structure entry, contains subaisles."""

    id: int
    display_code: str
    name: str
    subaisles: typing.List[Subaisle]

    @classmethod
    def from_db(cls, aisle: models.Aisle, subaisles: typing.List[Subaisle]) -> "AisleStructureEntry":
        """Convert a database Aisle to a structure entry."""
        return cls(
            id=aisle.id,
            display_code=aisle.code,
            name=aisle.name,
            subaisles=subaisles,
        )


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class ProductToLocate:
    """A product to locate in the Product Locations Table app."""

    id: int
    name: str
    vendor: str
    date_started: typing.Union[None, datetime.datetime, str] = attr.ib(
        converter=date_to_string_opt_converter, default=None
    )
    date_ended: typing.Union[None, datetime.datetime, str] = attr.ib(
        converter=date_to_string_opt_converter, default=None
    )
    details_url: str
    vendor_details_url: str
    subcategory: Subcategory
    location: typing.Optional["ProductLocation"]

    @classmethod
    def from_db(
        cls, product: ms_products.models.Product, location: typing.Optional[models.ProductLocation]
    ) -> "ProductToLocate":
        """Convert a database Product and Location to a ProductToLocate."""
        return cls(
            id=product.id,
            name=product.name,
            vendor=product.vendor.name,
            date_started=product.date_started,
            date_ended=product.date_ended,
            details_url=product.get_absolute_url(),
            vendor_details_url=product.vendor.get_absolute_url(),
            subcategory=Subcategory.from_db(product.subcategory),
            location=ProductLocation.from_db(location) if location else None,
        )


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class MapDTO:
    """A map data transfer object."""

    id: typing.Optional[int]
    width: int
    height: int
    date_started: typing.Union[None, datetime.datetime, str] = attr.ib(
        converter=date_to_string_opt_converter, default=None
    )
    date_ended: typing.Union[None, datetime.datetime, str] = attr.ib(
        converter=date_to_string_opt_converter, default=None
    )

    @classmethod
    def from_db(cls, db_map: models.Map) -> "MapDTO":
        """Convert a database Map to a MapDTO."""
        return cls(
            id=db_map.id,
            width=db_map.width,
            height=db_map.height,
            date_started=db_map.date_started,
            date_ended=db_map.date_ended,
        )


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class MapTileDTO:
    """A map tile data transfer object."""

    id: typing.Optional[int]
    x: int
    y: int
    tile_type: str
    subaisle: typing.Optional[Subaisle]
    color: typing.Optional[str]
    color_is_light: bool

    @classmethod
    def from_db(cls, db_tile: models.MapTile) -> "MapTileDTO":
        """Convert a database MapTile to a MapDTO."""
        return cls(
            id=db_tile.id,
            x=db_tile.x,
            y=db_tile.y,
            tile_type=db_tile.tile_type,
            subaisle=Subaisle.from_db(db_tile.subaisle) if db_tile.subaisle else None,
            color=db_tile.color,
            color_is_light=db_tile.color_is_light,
        )


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class ProductLocation:
    """A product location."""

    id: typing.Optional[int]
    tile: typing.Optional[MapTileDTO]
    subaisle: typing.Optional[Subaisle]
    is_auto: bool
    date_started: typing.Union[None, datetime.datetime, str] = attr.ib(
        converter=date_to_string_opt_converter, default=None
    )
    date_ended: typing.Union[None, datetime.datetime, str] = attr.ib(
        converter=date_to_string_opt_converter, default=None
    )

    @classmethod
    def from_db(cls, location: models.ProductLocation) -> "ProductLocation":
        """Convert a database ProductLocation to an API ProductLocation."""
        return cls(
            id=location.id,
            tile=MapTileDTO.from_db(location.tile) if location.tile else None,
            subaisle=Subaisle.from_db(location.subaisle) if location.subaisle else None,
            is_auto=location.is_auto,
            date_started=location.date_started,
            date_ended=location.date_ended,
        )


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class ProductLocationChange:
    """A change in the product location."""

    product: ProductToLocate
    tile: typing.Optional[MapTileDTO]
    subaisle: typing.Optional[Subaisle]
    revert_auto: bool = False
    delete_location: bool = False


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class ProductLocationGetResponse:
    """A response to a request for product locations."""

    products: typing.List[ProductToLocate]
    filter: typing.Union[str, ProductLocationFilter] = attr.ib(converter=enum_get_value)
    page: int
    totalPages: int


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class ProductGroupsGetResponse:
    """A response to a request for product groups."""

    map: MapDTO
    tiles: typing.List[MapTileDTO]
    categoryStructure: typing.List[CategoryStructureEntry]
    aisleStructure: typing.List[AisleStructureEntry]
    subaisles: typing.List[Subaisle]


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class ProductLocationChangeDescription:
    """A description of product location changes."""

    date: str
    changes: typing.List[ProductLocationChange]


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class ProductLocationChangeResponse:
    """A response to product location chanegs."""

    success: bool
    message: str
    warning: bool = False


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class MapSaveRequest:
    """A map save request."""

    map: MapDTO
    tiles: typing.List[MapTileDTO]
    date: str


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class MapSaveResponse:
    """A response to map saves."""

    success: bool
    message: str
    warning: bool = False
    map: typing.Optional[MapDTO] = None
    tiles: typing.List[MapTileDTO] = attr.ib(factory=list)


def build_vue_aisles_structure(store):
    """Build a Vue-friendly aisles structure."""
    db_struct = build_aisles_structure(store, visible_only=True, include_counts=False)
    return [
        AisleStructureEntry.from_db(aisle, [Subaisle.from_db(sa) for sa in subaisles]) for aisle, subaisles in db_struct
    ]
