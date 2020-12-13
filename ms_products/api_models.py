"""Vue and extra models for ms_products."""

import typing

import attr

import ms_products.models
from ms_products.views.utils import build_categories_structure


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class SubcategoryStructureEntry:
    """A subcategory structure entry."""

    id: int
    name: str

    @classmethod
    def from_db(cls, sc: ms_products.models.Subcategory) -> "SubcategoryStructureEntry":
        """Convert a database Subcategory to a structure entry."""
        return cls(id=sc.id, name=sc.name)


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class CategoryStructureEntry:
    """A category structure entry, contains subcategories."""

    id: int
    name: str
    subcategories: typing.List[SubcategoryStructureEntry]

    @classmethod
    def from_db(
        cls, cat: ms_products.models.Category, subcategories: typing.List[SubcategoryStructureEntry]
    ) -> "CategoryStructureEntry":
        """Convert a database Category to a structure entry."""
        return cls(id=cat.id, name=cat.name, subcategories=subcategories)


def build_vue_categories_structure():
    """Build a Vue-friendly categories structure."""
    db_struct = build_categories_structure(visible_only=True, include_counts=False)
    return [
        CategoryStructureEntry.from_db(cat, [SubcategoryStructureEntry.from_db(sc) for sc in subcats])
        for cat, subcats in db_struct
    ]
