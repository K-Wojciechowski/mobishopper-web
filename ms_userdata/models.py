"""Models for user data."""
import datetime
import typing
from uuid import uuid4

import django.utils.formats
import django.utils.timezone
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.html import format_html

from ms_baseline import constants
from ms_baseline.models import CheckoutApiKey, DateTrackedModel, MsUser, PriceField, Store
from ms_deals.models import Coupon, CouponSet
from ms_products.models import Product


class CouponUse(DateTrackedModel):
    """The use of a coupon by a user."""

    uuid = models.UUIDField(default=uuid4, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, default=None)
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT)
    is_used = models.BooleanField(default=False)
    used_date = models.DateTimeField(default=None, null=True)
    used_with = models.ForeignKey(CheckoutApiKey, on_delete=models.SET_NULL, null=True)
    valid_until = models.DateTimeField()

    def is_still_valid(self, now=None) -> bool:
        """Check if a coupon set is still valid (can be shown to a user)."""
        if not now:
            now = django.utils.timezone.now()
        return now <= self.valid_until


class CouponSetUse(DateTrackedModel):
    """The use of a coupon set by a user."""

    uuid = models.UUIDField(default=uuid4, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, default=None)
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    coupon_set = models.ForeignKey(CouponSet, on_delete=models.PROTECT)
    is_used = models.BooleanField(default=False)
    used_date = models.DateTimeField(default=None, null=True)
    used_with = models.ForeignKey(CheckoutApiKey, on_delete=models.SET_NULL, null=True)
    valid_until = models.DateTimeField()

    def is_still_valid(self, now=None) -> bool:
        """Check if a coupon set is still valid (can be shown to a user)."""
        if not now:
            now = django.utils.timezone.now()
        return now <= self.valid_until


class ShoppingList(DateTrackedModel):
    """A user’s shopping list."""

    name = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    price_cached = PriceField(default=0)
    store = models.ForeignKey(Store, on_delete=models.PROTECT)
    sharing_uuid = models.UUIDField(default=None, null=True, blank=True, unique=True)
    shared_with = models.ManyToManyField(MsUser, related_name="shared_with", blank=True)
    completion = models.IntegerField(default=0)  # 0-100

    def upgrade_products(self, allow_ignore=True):
        """Upgrade all products on a shopping list."""
        now = django.utils.timezone.now()
        ignore_after = now - datetime.timedelta(minutes=constants.IGNORE_SHOPPING_LIST_MIGRATIONS_MINUTES)
        if allow_ignore and self.date_modified >= ignore_after:
            return False
        entries: typing.List[ShoppingListEntry] = list(self.entries.all())
        products_in_entries = {e.product.id: e for e in entries}
        any_changes = False
        for e in entries:
            new_product = e.try_upgrade(now)
            if not new_product:
                continue
            other = products_in_entries.get(new_product.id)
            if other:
                # User has two entries for the same product. This is a very rare case, but still possible.
                # This conflict will be resolved by removing the older product.
                if other.date_added < e.date_added:
                    other.delete()
                else:
                    e.delete()
                    any_changes = True
                    continue

            e.product_upgraded_from = e.product
            e.product = new_product
            e.save()
            any_changes = True
            products_in_entries[e.product.id] = e
        self.save()  # calls update_shopping_list_price_completion
        return any_changes

    def update_price_completion(self):
        """Update the price and completion of this shopping list."""
        now = django.utils.timezone.now()
        entry_count = self.entries.count()
        if entry_count:
            self.price_cached = sum(e.amount * e.product.get_price(self.store, now) for e in self.entries.all())
            self.completion = round(self.entries.filter(bought=True).count() * 100 / entry_count)
        else:
            self.price_cached = 0
            self.completion = 0
        return self.price_cached, self.completion

    def get_sharing_url(self, request=None):
        """Get the sharing URL for a shopping list."""
        if not self.sharing_uuid:
            return None
        path = reverse("ms_userdata_share:shared_list", args=(self.sharing_uuid,))
        if request:
            return request.build_absolute_uri(path)

    def __str__(self):
        """Return the name of the list."""
        return self.name

    def can_access(self, user):
        """Check if the given user can access this list."""
        return user == self.user or bool(self.shared_with.filter(id=user.id))
        pass


class ShoppingListEntry(DateTrackedModel):
    """An entry on a user’s shopping list."""

    list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name="entries")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    amount = models.DecimalField(decimal_places=3, max_digits=10)  # Normalized to the product price
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bought = models.BooleanField(default=False)
    product_upgraded_from = models.ForeignKey(
        Product, on_delete=models.SET_NULL, related_name="+", blank=True, null=True
    )

    @property
    def price(self):
        """Get the price of the product."""
        return self.product.price * self.amount

    def upgrade_and_save(self, now=None):
        """Try to upgrade the product, and save if applicable."""
        if now is None:
            now = django.utils.timezone.now()
        orig_product = self.product
        while self.product.replaced_by is not None and not self.product.in_effect(now):
            self.product = self.product.replaced_by
        if self.product != orig_product:
            self.product_upgraded_from = orig_product
            self.save()

    def try_upgrade(self, now=None) -> typing.Optional[Product]:
        """Try to upgrade the product. Return new product or none."""
        if now is None:
            now = django.utils.timezone.now()
        orig_product = self.product
        product = self.product
        while product.replaced_by is not None and not product.in_effect(now):
            product = product.replaced_by
        if product != orig_product:
            return product

    def __str__(self):
        """Return the name of the entry."""
        return f"{self.product.name} @ {self.list.name}"

    class Meta:
        constraints = [models.UniqueConstraint(fields=["list", "product"], name="unique_product")]


class ShoppingListInvite(DateTrackedModel):
    """An invitation to join a shopping list."""

    id = models.UUIDField(default=uuid4, primary_key=True)
    list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    email = models.EmailField()
    used = models.BooleanField(default=False)

    def get_expiry_date(self):
        """Get the shopping list expiry date."""
        return self.date_added + datetime.timedelta(days=constants.INVITE_EXPIRATION_DAYS)

    def is_expired(self):
        """Check if the invite is expired."""
        return self.used or django.utils.timezone.now() > self.get_expiry_date()

    def get_invite_url(self, request=None):
        """Get the invite URL for a shopping list."""
        path = reverse("ms_userdata_share:accept_invite", args=(self.id,))
        if request:
            return request.build_absolute_uri(path)
        else:
            return path

    def send_email(self, request=None, user=None):
        """Send the invite via e-mail."""
        if not user:
            user: MsUser = self.list.user

        full_name = user.get_full_name()
        link = self.get_invite_url(request)
        date = django.utils.formats.date_format(self.get_expiry_date(), "DATETIME_FORMAT")

        plain_msg = settings.MOBISHOPPER_INVITE_PLAINTEXT.format(user=full_name, link=link, date=date)
        html_msg = format_html(settings.MOBISHOPPER_INVITE_HTML, user=full_name, link=link, date=date)
        send_mail(
            settings.MOBISHOPPER_INVITE_SUBJECT.format(user=full_name),
            plain_msg,
            settings.MOBISHOPPER_EMAIL,
            [self.email],
            html_message=html_msg,
            fail_silently=False,
        )

    def __str__(self):
        """Return name of invite."""
        return f"{self.list.name} {self.email}"


@receiver(models.signals.pre_save, sender=ShoppingList)
def update_shopping_list_price_completion(instance: ShoppingList, **kwargs):
    """Update a shopping list’s price and completion before saving."""
    instance.update_price_completion()


@receiver(models.signals.post_save, sender=ShoppingListEntry)
def update_shopping_list_entry_owner_price_save(instance: ShoppingListEntry, **kwargs):
    """Update a shopping list’s price after saving an entry."""
    instance.list.save()  # calls update_shopping_list_price_completion


@receiver(models.signals.post_delete, sender=ShoppingListEntry)
def update_shopping_list_entry_owner_price_delete(instance: ShoppingListEntry, **kwargs):
    """Update a shopping list’s price after saving an entry."""
    instance.list.save()  # calls update_shopping_list_price_completion
