"""Constants used in ms_baseline."""
from django.db.models import F
from django.utils.translation import gettext_lazy as _

LOCAL_PERMISSION_CHOICES = (
    ("can_manage_products", _("Can manage products")),
    ("can_manage_maps", _("Can manage maps")),
    ("can_manage_deals", _("Can manage deals")),
    ("can_manage_employees", _("Can manage employees")),
    ("can_view_statistics", _("Can view statistics")),
)

LOCAL_PERMISSION_TABLE_TITLES = (
    ("can_manage_products", _("Products")),
    ("can_manage_maps", _("Maps")),
    ("can_manage_deals", _("Deals")),
    ("can_manage_employees", _("Employees")),
    ("can_view_statistics", _("Statistics")),
)

GLOBAL_PERMISSION_CHOICES = (
    ("can_manage_global_products", _("Can manage global products")),
    ("can_manage_global_deals", _("Can manage global deals")),
    ("can_view_global_statistics", _("Can view global statistics")),
    ("can_manage_users", _("Can manage users")),
    ("can_manage_stores", _("Can manage stores")),
)

ACCOUNT_TYPES_CHOICES = (
    ("is_manager", _("Is manager")),
    ("is_global_manager", _("Is global manager")),
    ("is_superuser", _("Is system administrator")),
)

STORE_VISIBILITY_CHOICES = (
    ("visible", _("Only visible stores")),
    ("hidden", _("Only hidden stores")),
    ("all", _("Show all stores")),
)

LOCAL_PERMISSIONS = tuple(i[0] for i in LOCAL_PERMISSION_CHOICES)
GLOBAL_PERMISSIONS = tuple(i[0] for i in GLOBAL_PERMISSION_CHOICES)
ACCOUNT_TYPES = tuple(i[0] for i in ACCOUNT_TYPES_CHOICES)
LOCAL_PERMISSIONS_SHORT_TITLES = tuple(i[1] for i in LOCAL_PERMISSION_TABLE_TITLES)

LOCAL_USER_DATA = ("email", "first_name", "last_name")
ALL_USER_DATA = tuple(list(LOCAL_USER_DATA) + list(GLOBAL_PERMISSIONS) + list(ACCOUNT_TYPES))

LINK_FMT = '<a href="{0}">{1}</a>'
FULL_PATH_FMT = "{0} › {1}"

ORDER_NEWEST_FIRST = (
    F("date_started").desc(nulls_last=True),
    F("date_added").desc(nulls_last=True),
    F("date_modified").desc(nulls_last=True),
    F("name").asc(nulls_last=True),
)

DEFAULT_MAP_SIZE = 10

INVITE_EXPIRATION_DAYS = 3
COUPON_USE_VALIDITY_MINUTES = 20
IGNORE_SHOPPING_LIST_MIGRATIONS_MINUTES = 15
DECIMAL_SEPARATOR = ","
