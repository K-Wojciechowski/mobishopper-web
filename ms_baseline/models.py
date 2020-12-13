"""Baseline models for MobiShopper."""
import datetime
import functools
import logging
import typing
from uuid import uuid4

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from ms_baseline import constants

logger = logging.getLogger("ms_baseline.models")


class BaseModel(models.Model):
    """A base model for MobiShopper."""

    def save_with_error_message(self, request):
        """Save a model with a message."""
        # noinspection PyBroadException
        try:
            self.save()
            return True
        except ValidationError as e:
            logger.exception(f"Failed to save {self} due to a validation error.")
            if request:
                messages.error(request, _("Failed to save changes: {0}").format(e))
        except Exception:
            logger.exception(f"Failed to save {self}.")
            if request:
                messages.error(request, _("Failed to save changes."))

        return False

    def html_link(self):
        """Return HTML link to object."""
        return format_html(constants.LINK_FMT, self.get_absolute_url(), str(self))

    def save_with_message(self, request):
        """Save a model with an error message."""
        success = self.save_with_error_message(request)
        if success and request:
            messages.info(request, _("Changes saved."))
        return success

    def get_absolute_url(self):
        """Get the absolute URL to this object."""
        return "#unknown"

    class Meta:
        abstract = True


class DateTrackedModel(BaseModel):
    """Abstract model whose added/modified dates are tracked."""

    date_added = models.DateTimeField(_("date added"), auto_now_add=True)
    date_modified = models.DateTimeField(_("date modified"), auto_now=True)

    class Meta:
        abstract = True


class DateRangedTrackedModel(DateTrackedModel):
    """Abstract model with a start/end date."""

    date_started = models.DateTimeField(_("valid from"), null=True, blank=True)
    date_ended = models.DateTimeField(_("valid until"), null=True, blank=True)

    REVISION_MIGRATIONS: typing.List[typing.Tuple[typing.Type["DateRangedTrackedModel"], str]] = []

    def in_effect(self, when: typing.Union[None, datetime.datetime] = None):
        """Check if the current instance is in effect at a specified date."""
        if not when:
            when = timezone.now()
        return (self.date_started is None or typing.cast(datetime.datetime, self.date_started) <= when) and (
            self.date_ended is None or typing.cast(datetime.datetime, self.date_ended) > when
        )

    def clean(self):
        """Validate that dates make sense."""
        if self.date_started and self.date_ended and self.date_started >= self.date_ended:
            raise ValidationError(_("The validity end date is earlier than the start date."))

    def save_as_replacement(self, request, old_obj: "DateRangedTrackedModel", *, quiet: bool = False):
        """Save this as a new object as the old object’s replacement."""
        success = True
        if self.date_started is None:
            self.date_started = timezone.now()
        if old_obj.date_ended is None or old_obj.date_ended > self.date_started:
            old_obj.date_ended = self.date_started
            if old_obj.date_started and old_obj.date_ended and old_obj.date_started >= old_obj.date_ended:
                old_obj.date_started = old_obj.date_ended
            success = old_obj.save_with_error_message(request)
        if not success:
            return False

        if quiet:
            self.save_with_error_message(request)
        else:
            self.save_with_message(request)

        if not hasattr(old_obj, "replaced_by"):
            self.migrate_with_revision(request, old_obj)
            return True

        old_obj.replaced_by = self
        try:
            old_obj.save()
        except Exception as e:
            logger.exception(
                f"Saved new object {self} ({self.__class__} #{self.id}), but failed to update #{old_obj.id} with replacement."
            )
            if request is not None:
                messages.warning(request, _("There was an issue saving changes to this object’s replacement."))
        self.migrate_with_revision(request, old_obj)
        return True

    def migrate_with_revision(self, request, old_obj: "DateRangedTrackedModel"):
        """Migrate an object from old_obj to self, based on the list of REVISION_MIGRATIONS."""
        now = timezone.now()

        for cls, field in self.REVISION_MIGRATIONS:
            if not issubclass(cls, DateRangedTrackedModel):
                instances = cls.objects.filter(**{field: old_obj})
                for instance in instances:
                    try:
                        setattr(instance, field, self)
                        instance.save_with_error_message(request)
                    except Exception as e:
                        if request is not None:
                            messages.warning(request, _("There was an issue migrating objects with revisions."))
                        logger.exception(
                            f"While migrating {self} ({self.__class__} #{self.id}), the dependent object {cls} #{instance.id} failed to save."
                        )
                continue

            instances = cls.objects.filter(Q(date_ended=None) | Q(date_ended__gt=now), **{field: old_obj})
            for instance in instances:
                old_id = instance.id
                try:
                    # Save as new object by setting pk and id to None
                    instance.pk = None
                    instance.id = None
                    instance.date_started = self.date_started
                    if instance.date_started and instance.date_ended and instance.date_ended < instance.date_started:
                        continue  # Migrating does not make sense.
                    setattr(instance, field, self)
                    instance.save_with_error_message(request)

                    old_instance = cls.objects.get(id=old_id)
                    old_instance.date_ended = self.date_started
                    if (
                        old_instance.date_started
                        and old_instance.date_ended
                        and old_instance.date_started > old_instance.date_ended
                    ):
                        old_instance.date_started = old_instance.date_ended
                    if hasattr(old_instance, "replaced_by"):
                        old_instance.replaced_by = instance
                    old_instance.save_with_error_message(request)

                    instance.migrate_with_revision(request, old_instance)
                except Exception as e:
                    if request is not None:
                        messages.warning(request, _("There was an issue migrating objects with revisions."))
                    logger.exception(
                        f"While migrating {self} ({self.__class__} #{self.id}), the dependent object {cls} #{old_id} failed to save."
                    )

    class Meta:
        abstract = True


class Store(DateTrackedModel):
    """A store."""

    name = models.CharField(_("name"), max_length=100)
    address = models.CharField(_("address"), max_length=150)
    city = models.CharField(_("city"), max_length=50)
    region_code = models.CharField(_("region code"), max_length=2)
    hidden = models.BooleanField(_("hidden"), default=False)

    def __str__(self):
        """Return name of the store."""
        return self.name

    def get_absolute_url(self):
        """Return absolute URL to the store."""
        return reverse("ms_baseline:stores_edit", args=(self.id,))


class MsUserManager(UserManager):
    """User manager for MsUser objects."""

    def _create_user(self, email, password, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class MsUser(AbstractUser, BaseModel):
    """A user identified by e-mail."""

    username = None
    email = models.EmailField(max_length=255, unique=True)

    first_name = models.CharField(_("first name"), max_length=150, blank=False)
    last_name = models.CharField(_("last name"), max_length=150, blank=False)

    default_store = models.ForeignKey(Store, on_delete=models.SET_NULL, blank=True, null=True)
    is_manager = models.BooleanField(_("is manager"), default=False)
    is_global_manager = models.BooleanField(_("is global manager"), default=False)
    can_manage_global_products = models.BooleanField(_("can manage global products"), default=False)
    can_manage_global_deals = models.BooleanField(_("can manage global deals"), default=False)
    can_view_global_statistics = models.BooleanField(_("can view global statistics"), default=False)
    can_manage_users = models.BooleanField(_("can manage users"), default=False)
    can_manage_stores = models.BooleanField(_("can manage stores"), default=False)

    objects = MsUserManager()
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def is_employee(self):
        """Check if the user is an employee."""
        return self.is_manager or self.is_global_manager or self.is_superuser

    @property
    def is_management_employee(self):
        """Check if the user is a management employee employee."""
        return self.is_manager or self.is_global_manager

    def get_profile(self):
        """Return the current user’s profile."""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.get_full_name(),
            "default_store_id": self.default_store_id,
        }


class UserStorePermission(BaseModel):
    """A permission for a user to manage stores."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("user"))
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name=_("store"))
    can_manage_products = models.BooleanField(_("can manage products"), default=True)
    can_manage_maps = models.BooleanField(_("can manage maps"), default=True)
    can_manage_deals = models.BooleanField(_("can manage deals"), default=False)
    can_manage_employees = models.BooleanField(_("can manage employees"), default=False)
    can_view_statistics = models.BooleanField(_("can view statistics"), default=False)


class CheckoutApiKey(DateTrackedModel):
    """An API key for checkouts."""

    name = models.CharField(_("name"), max_length=100)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name=_("store"))
    key = models.UUIDField(default=uuid4)
    is_active = models.BooleanField(_("is active"), default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name=_("user"))

    def __str__(self):
        """Return name of the key."""
        return self.name

    def get_absolute_url(self):
        """Return absolute URL to the key."""
        return reverse("ms_baseline:checkout_api_keys_edit", args=(self.id,))


PriceField = functools.partial(models.DecimalField, decimal_places=2, max_digits=10)


@receiver(models.signals.pre_save, sender=BaseModel)
def ensure_full_clean(instance: BaseModel, **kwargs):
    """Ensure all models are validated."""
    instance.full_clean()
