"""Forms for ms_deals."""
import typing

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ms_baseline.form_utils import (
    BaseForm,
    BaseModelForm,
    IsoDateTimePickerInput,
    LaxMultipleChoiceField,
    inline_textinput,
)
from ms_baseline.models import DateRangedTrackedModel
from ms_deals.models import Coupon, CouponSet, Deal


class DealCouponSearchForm(BaseForm):
    """A form used for filtering deals and coupons."""

    name = forms.CharField(label=_("Name"), required=False, widget=inline_textinput(_("Name")))
    product = forms.CharField(label=_("Product name"), required=False, widget=inline_textinput(_("Product name")))
    valid_at = forms.DateTimeField(
        label=_("Valid at"), required=False, widget=IsoDateTimePickerInput, initial=timezone.now
    )
    is_store = forms.BooleanField(label=_("Is store-specific"), required=False)


class ValidDateChangeForm(BaseForm):
    """A form used for changing validity dates."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=True, widget=IsoDateTimePickerInput)
    date_ended = forms.DateTimeField(label=_("Valid until"), required=False, widget=IsoDateTimePickerInput)


class ValidDateNameChangeForm(ValidDateChangeForm):
    """A form used for changing validity dates and names."""

    name = forms.CharField(label=_("Deal name"), required=True)


class ValidDateModelForm(BaseModelForm):
    """An abstract form used for changing validity dates."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=True, widget=IsoDateTimePickerInput)
    date_ended = forms.DateTimeField(label=_("Valid until"), required=False, widget=IsoDateTimePickerInput)


class DealAddForm(ValidDateModelForm):
    """A form used to add a deal."""

    class Meta:
        model = Deal
        fields = ["name", "product", "price", "is_global", "stores", "date_started", "date_ended"]
        help_text = {
            "product": _(
                "You can also find the product with product search, and use the Deals tab on the product page."
            )
        }


class CouponAddForm(ValidDateModelForm):
    """A form used to add a coupon."""

    class Meta:
        model = Coupon
        fields = [
            "name",
            "product",
            "price",
            "one_use",
            "require_account",
            "is_global",
            "stores",
            "date_started",
            "date_ended",
        ]
        help_text = {
            "product": _(
                "You can also find the product with product search, and use the Deals tab on the product page."
            )
        }


class CouponSetAddForm(ValidDateModelForm):
    """A form used to add a coupon set."""

    class Meta:
        model = CouponSet
        fields = ["name", "coupons", "one_use", "require_account", "is_global", "stores", "date_started", "date_ended"]


AddFormType = typing.Union[DealAddForm, CouponAddForm, CouponSetAddForm]
