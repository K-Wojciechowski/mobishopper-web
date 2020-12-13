"""Constants for ms_products."""
from django.utils.translation import gettext_lazy as _

UNIT_CHOICES = (("1", _("pc")), ("kg", _("kg")), ("dag", _("dag")), ("g", _("g")), ("L", _("L")), ("mL", _("mL")))

META_UNITS_CHOICES = (
    ("_number", _("number")),
    ("_str", _("text")),
    ("_bool", _("yes/no")),
    ("_custom_set", _("custom, from list")),
    ("_user", _("custom, user-provided")),
    ("weight", _("weight")),
    ("volume", _("volume")),
    ("area", _("area")),
    ("size", _("size")),
    ("energy", _("energy")),
)

META_UNITS_CHOICES_DICT = dict(META_UNITS_CHOICES)

UNIT_GROUPS = {
    "_number": [],
    "_str": [],
    "_bool": [_("yes"), _("no")],
    "_user": [],
    "weight": ["kg", "dag", "g"],
    "volume": ["m³", "dm³", "cm³", "L", "mL"],
    "area": ["m²", "dm²", "cm²"],
    "size": ["m", "dm", "cm", "mm"],
    "energy": ["kJ", "kcal"],
}

PREFETCH_PRODUCT_BASIC = ("vendor", "subcategory", "subcategory__parent", "replaced_by")
PREFETCH_SHOPPING_LIST = ["entries", "entries__product"] + ["entries__product__" + i for i in PREFETCH_PRODUCT_BASIC]
