"""Models for product management."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from ms_baseline import constants
from ms_baseline.models import DateRangedTrackedModel, DateTrackedModel, PriceField, Store
from ms_baseline.utils import filter_in_effect, format_decimal
from ms_products.constants import META_UNITS_CHOICES, META_UNITS_CHOICES_DICT, UNIT_CHOICES, UNIT_GROUPS
from ms_products.utils import get_price_per_amount_str


class Category(DateTrackedModel):
    """A product category."""

    name = models.CharField(_("name"), max_length=50)
    description = models.TextField(_("description"), blank=True)
    visible = models.BooleanField(_("visible"), default=True)

    def __str__(self):
        """Return name of the category."""
        return self.name

    def get_absolute_url(self):
        """Get absolute URL to the category."""
        return reverse("ms_products:categories_search", args=(self.id,))


class Subcategory(DateTrackedModel):
    """A product subcategory."""

    name = models.CharField(_("name"), max_length=50)
    description = models.TextField(_("description"), blank=True)
    visible = models.BooleanField(_("visible"), default=True)
    parent = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=_("parent"))

    def __str__(self):
        """Return name of the subcategory."""
        return self.name

    def get_absolute_url(self):
        """Get absolute URL to the subcategory."""
        return reverse("ms_products:subcategories_search", args=(self.id,))

    def full_path_html(self):
        """Return HTML link to category and subcategory."""
        return format_html(constants.FULL_PATH_FMT, self.parent.html_link(), self.html_link())


class GenericSubaisle(DateTrackedModel):
    """A generic product subaisle, upon which stores can base their subaisles."""

    name = models.CharField(_("name"), max_length=50)
    description = models.TextField(_("description"))
    subcategories = models.ManyToManyField(Subcategory, blank=False, verbose_name=_("subcategories"))

    def __str__(self):
        """Return name of the subaisle."""
        return self.name

    def get_aboslute_url(self):
        """Get absolute URL to the subaisle."""
        return reverse("ms_products:subaisles_show", args=(self.id,))


class Vendor(DateRangedTrackedModel):
    """A vendor of products."""

    name = models.CharField(_("name"), max_length=100)
    logo = models.ImageField(_("logo"), blank=True)
    description = models.TextField(_("description"), blank=True)
    website = models.URLField(_("website"), blank=True)
    replaced_by = models.ForeignKey(
        "Vendor", on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("replaced by")
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_("store"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("user")
    )

    def __str__(self):
        """Return name of the vendor."""
        return self.name

    def get_absolute_url(self):
        """Get absolute URL to the vendor."""
        return reverse("ms_products:vendors_show", args=(self.id,))

    @property
    def is_store_specific(self):
        """Check if the vendor is store-specific."""
        return self.store is not None


class ProductGroup(DateRangedTrackedModel):
    """A group of products.

    Products can be in a group, if they are variants of each other.
    They can differ by amount, color, container, or other properties.
    """

    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    photo = models.ImageField(_("photo"), blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, verbose_name=_("vendor"))
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_("store"))
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, verbose_name=_("subcategory"))
    replaced_by = models.ForeignKey(
        "ProductGroup", on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("replaced by")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("user")
    )

    def __str__(self):
        """Return name of the group."""
        return self.name

    def get_absolute_url(self):
        """Get absolute URL to the group."""
        return reverse("ms_products:groups_show", args=(self.id,))

    @property
    def is_store_specific(self):
        """Check if the group is store-specific."""
        return self.store is not None


class StandardMetaField(DateTrackedModel):
    """A standard meta field (property)."""

    name = models.CharField(_("name"), max_length=50)
    expected_units = models.CharField(_("expected units"), choices=META_UNITS_CHOICES, max_length=16, blank=False)
    # list of strings
    expected_units_custom_set = models.JSONField(_("expected units (custom names)"), default=list, blank=True)
    subcategories_required = models.ManyToManyField(
        Subcategory, related_name="+", verbose_name=_("subcategories where required"), blank=True
    )
    subcategories_recommended = models.ManyToManyField(
        Subcategory, related_name="+", verbose_name=_("subcategories where recommended"), blank=True
    )

    def __str__(self):
        """Return name of the property."""
        return self.name

    @property
    def slug(self):
        """Generate a slug, used to uniquely identify properties."""
        return f"{slugify(self.name)}-{self.id}"

    @property
    def expected_units_names(self) -> list:
        """Get names of expected units."""
        if self.expected_units == "_custom_set":
            return self.expected_units_custom_set

        return UNIT_GROUPS.get(self.expected_units, [])

    @property
    def expected_units_friendly_name(self):
        """Get friendly name of expected units."""
        return META_UNITS_CHOICES_DICT[self.expected_units]

    def get_absolute_url(self):
        """Get absolute URL to the property."""
        return reverse("ms_products:properties_edit", args=(self.id,))


class Product(DateRangedTrackedModel):
    """A product."""

    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, verbose_name=_("vendor"))
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, verbose_name=_("subcategory"))
    photo = models.ImageField(_("photo"), blank=True)
    price = PriceField(_("price"))
    amount = models.DecimalField(_("amount"), decimal_places=3, max_digits=10)
    amount_unit = models.CharField(_("amount unit"), choices=UNIT_CHOICES, max_length=3)
    any_amount = models.BooleanField(_("any amount possible"), default=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, blank=True, null=True, verbose_name=_("store"))
    # Stores slug and unit data (name, text, slug, value, unit)
    extra_metadata_raw = models.JSONField(default=list, blank=True, verbose_name=_("properties"))
    # Stores only human-friendly names and formatted values
    extra_metadata_dict = models.JSONField(default=dict, blank=True, verbose_name=_("properties (cache)"))
    replaced_by = models.ForeignKey(
        "Product", on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("replaced by")
    )
    group = models.ForeignKey(
        ProductGroup, on_delete=models.SET_NULL, blank=True, null=True, related_name="products", verbose_name=_("group")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("user")
    )

    def clean(self):
        """Validate that prices make sense."""
        super().clean()
        if self.price <= 0:
            raise ValidationError(_("The price must be greater than 0."))

    def amount_str(self):
        """Return amount as string."""
        amount_num = format_decimal(self.amount)
        if self.amount_unit == "1":
            return ngettext("{amount} pc", "{amount} pcs", self.amount).format(amount=amount_num)
        else:
            return f"{amount_num} {self.amount_unit}"

    def price_per_amount_str(self):
        """Return price per amount as string."""
        return get_price_per_amount_str(self.price, self.amount, self.amount_unit)

    def build_extra_metadata_dict(self):
        """Build a dict of extra metadata."""
        if self.extra_metadata_raw:
            return self.build_extra_metadata_dict_from_raw(self.extra_metadata_raw)
        else:
            return {}

    def get_price(self, store=None, now=None):
        """Get the price of this product in a given store at a given time."""
        if store is None:
            return self.price
        override: LocalProductOverride = (
            self.localproductoverride_set.filter(filter_in_effect(now), store=store).order_by("price").first()
        )
        return override.price if override else self.price

    @staticmethod
    def build_extra_metadata_dict_from_raw(extra_metadata_raw):
        """Build a dict of extra metadata from raw metadata."""
        return {item["name"]: item["text"] for item in extra_metadata_raw}

    @property
    def extra_metadata_tuples(self):
        """Build a list-of-tuples of extra metadata."""
        if self.extra_metadata_raw:
            return [(item["name"], item["text"]) for item in self.extra_metadata_raw]
        else:
            return []

    @property
    def has_extra_metadata(self):
        """Check if the product has extra metadata."""
        return bool(self.extra_metadata_raw)

    def get_absolute_url(self):
        """Get absolute URL to the product."""
        return reverse("ms_products:show_edit", args=(self.id,))

    @property
    def is_store_specific(self):
        """Check if the product is store-specific."""
        return self.store is not None

    def __str__(self):
        """Return name of the product."""
        return self.name


class LocalProductOverride(DateRangedTrackedModel):
    """A store-specific product override."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("product"))
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name=_("store"))
    available = models.BooleanField(_("is available"), default=True)
    price = PriceField(_("price"), blank=True, null=True)
    note = models.TextField(_("note"), blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("user")
    )

    def clean(self):
        """Validate that prices make sense."""
        super().clean()
        if self.price <= 0:
            raise ValidationError(_("The price must be greater than 0."))


@receiver(models.signals.pre_save, sender=Product)
def update_extra_metadata_dict(instance: Product, **kwargs):
    """Update extra_metadata_dict on Product objects."""
    instance.extra_metadata_dict = instance.build_extra_metadata_dict()


@receiver(models.signals.post_save, sender=GenericSubaisle)
def propagate_generic_subaisle(instance: GenericSubaisle, **kwargs):
    """Propagate changes from a generic subaisle to subaisles in stores."""
    from ms_maps.models import Subaisle

    subaisles = Subaisle.objects.filter(generic_subaisle=instance)
    for subaisle in subaisles:
        subaisle: Subaisle
        subaisle.update_from_generic(instance)
        subaisle.save()


from ms_deals.models import Coupon as _Coupon
from ms_deals.models import Deal as _Deal
from ms_maps.models import ProductLocation as _ProductLocation

Product.REVISION_MIGRATIONS = [
    (LocalProductOverride, "product"),
    (_Deal, "product"),
    (_Coupon, "product"),
    (_ProductLocation, "product"),
]
ProductGroup.REVISION_MIGRATIONS = [(Product, "group")]
Vendor.REVISION_MIGRATIONS = [(Product, "vendor")]
