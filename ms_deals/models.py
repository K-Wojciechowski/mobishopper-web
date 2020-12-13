"""Models for deals."""
import base64
import typing
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ms_baseline.models import DateRangedTrackedModel, PriceField, Store
from ms_products.models import Product
from ms_products.utils import get_price_per_amount_str


class Deal(DateRangedTrackedModel):
    """A special price for a product."""

    name = models.CharField(_("name"), max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("product"))
    is_global = models.BooleanField(_("is global"), default=False)
    stores = models.ManyToManyField(Store, verbose_name=_("stores"), blank=True)
    price = PriceField(_("price"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("user")
    )

    def clean(self):
        """Validate that prices make sense."""
        super().clean()
        if self.price <= 0:
            raise ValidationError(_("The price must be greater than 0."))

    def applies_in(self, store):
        """Check if a deal applies in a given store."""
        return applies_in(self, store)

    @property
    def price_per_amount_str(self):
        """Return price per amount as string."""
        return get_price_per_amount_str(self.price, self.product.amount, self.product.amount_unit)

    def get_absolute_url(self):
        """Get absolute URL of a deal."""
        return reverse("ms_deals:deals_show_edit", args=(self.id,))

    def __str__(self):
        """Return name of deal."""
        return self.name


class Coupon(DateRangedTrackedModel):
    """A coupon for a product."""

    uuid = models.UUIDField(_("coupon code"), default=uuid4, editable=False)
    name = models.CharField(_("name"), max_length=100)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("product"))
    is_global = models.BooleanField(_("is global"), default=False)
    stores = models.ManyToManyField(Store, verbose_name=_("stores"), blank=True)
    price = PriceField(_("price"))
    one_use = models.BooleanField(_("is one use only"), default=True)
    require_account = models.BooleanField(_("require log in"), default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("user")
    )

    def clean(self):
        """Validate that prices make sense."""
        super().clean()
        if self.price <= 0:
            raise ValidationError(_("The price must be greater than 0."))

    def applies_in(self, store):
        """Check if a coupon applies in a given store."""
        return applies_in(self, store)

    def is_usable(self, user, now=None) -> typing.Tuple[bool, typing.Optional[str]]:
        """Check if this coupon is usable by the specified user."""
        from ms_userdata.models import CouponUse

        return is_coupon_usable(self, user, CouponUse, "coupon", now)

    def generate_coupon_qr_data(self, use):
        """Generate QR code data for a coupon."""
        return generate_coupon_coupon_set_qr_data(self, use, "c")

    @property
    def price_per_amount_str(self):
        """Return price per amount as string."""
        return get_price_per_amount_str(self.price, self.product.amount, self.product.amount_unit)

    def get_absolute_url(self):
        """Get absolute URL of a coupon."""
        return reverse("ms_deals:coupons_show_edit", args=(self.id,))

    def __str__(self):
        """Return name of coupon."""
        return self.name


class CouponSet(DateRangedTrackedModel):
    """A group of coupons, available under the same ID."""

    uuid = models.UUIDField(_("coupon code"), default=uuid4, editable=False)
    name = models.CharField(_("name"), max_length=100)
    one_use = models.BooleanField(_("is one use only"), default=True)
    require_account = models.BooleanField(_("require log in"), default=False)
    coupons = models.ManyToManyField(Coupon, verbose_name=_("coupons"), blank=False)
    is_global = models.BooleanField(_("is global"), default=False)
    stores = models.ManyToManyField(Store, verbose_name=_("stores"), blank=True)

    def applies_in(self, store):
        """Check if a coupon set applies in a given store."""
        return applies_in(self, store)

    def is_usable(self, user, now=None) -> typing.Tuple[bool, typing.Optional[str]]:
        """Check if this coupon is usable by the specified user."""
        from ms_userdata.models import CouponSetUse

        return is_coupon_usable(self, user, CouponSetUse, "coupon_set", now)

    def generate_coupon_qr_data(self, use):
        """Generate QR code data for a set of coupons."""
        return generate_coupon_coupon_set_qr_data(self, use, "s")

    def get_absolute_url(self):
        """Get absolute URL of a coupon set."""
        return reverse("ms_deals:coupon_sets_show_edit", args=(self.id,))

    def __str__(self):
        """Return name of coupon set."""
        return self.name


DealsModelType = typing.Union[Deal, Coupon, CouponSet]


def applies_in(this: DealsModelType, store: typing.Union[None, Store, int]) -> typing.Optional[bool]:
    """Check if an object applies in a given store."""
    if this.is_global:
        return True
    if store is None:
        return None
    store_id: int = store if isinstance(store, int) else store.id
    return bool(this.stores.filter(id=store_id))


def generate_coupon_coupon_set_qr_data(coupon: typing.Union[Coupon, CouponSet], use, prefix: str):
    """Generate QR code data for a coupon or a coupon set."""
    if coupon.require_account and (not use.user or not use.user.is_authenticated):
        raise ValueError("User account required but not present")
    elif not use.user or not use.user.is_authenticated:
        data = f"{prefix}.{coupon.uuid}.anonymous.{use.uuid}"
    else:
        data = f"{prefix}.{coupon.uuid}.{use.user.id}.{use.uuid}"
    return base64.b64encode(data.encode("utf-8"))


def is_coupon_usable(
    coupon: typing.Union[Coupon, CouponSet], user, use_class, use_attr, now=None
) -> typing.Tuple[bool, typing.Optional[str]]:
    """Check if a coupon or coupon set is usable in a given store."""
    if not coupon.require_account and not coupon.one_use:
        return True, None
    if not user or not user.is_authenticated:
        return False, "require_account"
    if coupon.one_use:
        use_filters = {"user": user, use_attr: coupon}
        use = use_class.objects.filter(**use_filters).order_by("valid_until").last()
        if use and use.is_still_valid(now):
            return True, "activated_before_expiry"
        elif use:
            return False, "one_use"

    return True, None
