"""Map models for MobiShopper."""
import typing

import django.utils.timezone
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Index
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from mobishopper import settings
from ms_baseline.models import DateRangedTrackedModel, DateTrackedModel, Store
from ms_baseline.utils import filter_in_effect
from ms_products.models import GenericSubaisle, Product, Subcategory

TILE_TYPE_CHOICES = [
    ("entrance", "entrance"),
    ("exit", "exit"),
    ("ee", "entrance + exit"),
    ("register", "register"),
    ("product", "product"),
    ("subaisle", "subaisle"),
    ("space", "space"),
    ("block", "block"),
]


class Aisle(DateTrackedModel):
    """A store aisle."""

    name = models.CharField(_("name"), max_length=100)
    code = models.CharField(_("code"), blank=True, default="", max_length=10)
    description = models.TextField(_("description"), blank=True, default="")
    visible = models.BooleanField(_("visible"), default=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name=_("store"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("user")
    )

    @property
    def display_code(self):
        """Get the display code of the aisle."""
        return self.code

    def get_absolute_url(self):
        """Get absolute URL of the aisle."""
        return reverse("ms_maps:aisles_edit", args=(self.id,))

    def __str__(self):
        """Return the name of the aisle."""
        return self.name

    class Meta:
        ordering = ["code", "name"]


class Subaisle(DateTrackedModel):
    """A store subaisle, linked to a set of map tiles, and optionally subcategories."""

    name = models.CharField(_("name"), max_length=100)
    code = models.CharField(_("code"), blank=True, default="", max_length=10)
    description = models.TextField(_("description"), blank=True, default="")
    visible = models.BooleanField(_("visible"), default=True)
    parent = models.ForeignKey(Aisle, on_delete=models.CASCADE, verbose_name=_("parent"))
    generic_subaisle = models.ForeignKey(
        GenericSubaisle, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("global subaisle")
    )
    subcategories = models.ManyToManyField(Subcategory, blank=True, verbose_name=_("subcategories"))
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name=_("store"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("user")
    )

    def update_from_generic(self, generic_subaisle: typing.Optional[GenericSubaisle] = None):
        """Update this subaisle’s data from the generic subaisle."""
        if generic_subaisle is None:
            generic_subaisle = self.generic_subaisle
        if generic_subaisle is None:
            return
        self.name = generic_subaisle.name
        self.description = generic_subaisle.description
        self.subcategories.set(list(generic_subaisle.subcategories.all()))

    @property
    def display_code(self):
        """Get display code of the subaisle."""
        if not self.code:
            return ""
        elif not self.parent.code:
            return self.code
        return f"{self.parent.code}.{self.code}"

    @property
    def has_subcategories(self):
        """Check if the subaisle has subcategories assigned."""
        return self.subcategories.count() > 0

    def get_absolute_url(self):
        """Get absolute URL of the subaisle."""
        return reverse("ms_maps:subaisles_edit", args=(self.id,))

    def __str__(self):
        """Return the name of the aisle."""
        return self.name


class Map(DateRangedTrackedModel):
    """A store map."""

    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name=_("store"))
    width = models.IntegerField(_("width"))
    height = models.IntegerField(_("height"))
    replaced_by = models.ForeignKey(
        "Map", on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("replaced by")
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("user")
    )

    def get_absolute_url(self):
        """Get absolute URL of the map."""
        return reverse("ms_maps:maps_show", args=(self.id,))

    def __str__(self):
        """Return a description of the map."""
        tz = django.utils.timezone.get_current_timezone()
        dt = tz.normalize(self.date_started.astimezone(tz))
        return _("Map of {0} (since {1})").format(self.store, dt.strftime("%Y-%m-%d %H:%M"))


class MapTile(DateTrackedModel):
    """A store map tile."""

    map = models.ForeignKey(Map, on_delete=models.CASCADE, verbose_name=_("map"), related_name="tiles")
    x = models.IntegerField(_("x coordinate"))
    y = models.IntegerField(_("y coordinate"))
    tile_type = models.CharField(choices=TILE_TYPE_CHOICES, max_length=10, verbose_name=_("tile type"))
    subaisle = models.ForeignKey(Subaisle, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("subaisle"))
    color = models.CharField(_("color"), max_length=7, default="#ff0000")
    color_is_light = models.BooleanField(_("color is light"), default=True)

    def __str__(self):
        """Return a description of the map tile."""
        return "({0}, {1}) <{2}>".format(self.x, self.y, self.map)


class ProductLocation(DateRangedTrackedModel):
    """A location of a product, defined as a tile or subaisle."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("product"))
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name=_("store"))
    tile = models.ForeignKey(MapTile, on_delete=models.PROTECT, blank=True, null=True, verbose_name=_("tile"))
    subaisle = models.ForeignKey(Subaisle, on_delete=models.PROTECT, blank=True, null=True, verbose_name=_("subaisle"))
    is_auto = models.BooleanField(_("is auto-generated"), default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("user")
    )

    def clean(self):
        """Validate tile/subaisle values."""
        super().clean()
        if self.tile is None and self.subaisle is None:
            raise ValidationError("Either a tile or a subaisle must be provided.")
        if self.tile and self.subaisle and not self.tile.subaisle != self.subaisle:
            raise ValidationError("Tile is not connected to subaisle.")

    class Meta:
        indexes = [Index(fields=["product", "store"])]

    def __str__(self):
        """Return the name of the product and store."""
        return f"{self.product} @ {self.store}"

    def compute_auto_location(self, now=None, *, force=False, clear_tile=False):
        """Compute the automated location for a product."""
        if now is None:
            now = django.utils.timezone.now()
        if self.store is None:
            raise Exception("Missing store to generate location in")
        try:
            store_subaisle = Subaisle.objects.get(store=self.store, subcategories=self.product.subcategory_id)
            if self.is_auto or self.subaisle is None or force:
                self.subaisle = store_subaisle
                if not self.tile:
                    self.is_auto = True
            if clear_tile:
                self.tile = None
        except (Subaisle.DoesNotExist, Subaisle.MultipleObjectsReturned):
            self.is_auto = False
        return self.is_auto

    @classmethod
    def create_or_update_auto_location(cls, request, product: Product, store: Store, now=None, *, force=False):
        """Create or update a product location automatically."""
        if now is None:
            now = django.utils.timezone.now()
        try:
            obj = cls.objects.get(filter_in_effect(now), product=product, store=store)
            if obj.compute_auto_location(now, force=force, clear_tile=force):
                old_id = obj.id
                obj.id = None
                obj.pk = None
                obj.date_started = now
                old_obj = cls.objects.get(id=old_id)
                obj.save_as_replacement(request, old_obj, quiet=True)
                return obj
        except cls.DoesNotExist:
            return cls.create_auto_location(product, store, now, force=force)

    @classmethod
    def create_auto_location(cls, product: Product, store: Store, now=None, *, force=False):
        """Create a product location automatically."""
        if now is None:
            now = django.utils.timezone.now()
        obj = cls(product=product, store=store, date_started=now)
        if obj.compute_auto_location(now, force=force, clear_tile=force):
            obj.save()
            return obj


@receiver(models.signals.pre_delete, sender=Subaisle)
def delete_subaisles_from_tiles(instance: Subaisle, **kwargs):
    """Delete subaisles from map tiles (replace with Product shelf tiles)."""
    for t in instance.maptile_set.all():
        t.subaisle = None
        t.tile_type = "product"
        t.save()


@receiver(models.signals.pre_delete, sender=Aisle)
def delete_subaisles_before_aisles(instance: Aisle, **kwargs):
    """Delete subaisles before aisles so that they are removed from map tiles."""
    for subaisle in instance.subaisle_set.all():
        subaisle.delete()
