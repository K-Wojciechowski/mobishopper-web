"""Forms for ms_products."""
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import ms_products.constants
from ms_baseline.form_utils import (
    BaseForm,
    BaseModelForm,
    IsoDateTimePickerInput,
    LaxMultipleChoiceField,
    inline_textinput,
)
from ms_products.models import (
    Category,
    GenericSubaisle,
    LocalProductOverride,
    Product,
    ProductGroup,
    StandardMetaField,
    Subcategory,
    Vendor,
)

SELECT2_MEDIA_CSS = {
    "all": ("https://cdn.jsdelivr.net/npm/select2@4.1.0-beta.1/dist/css/select2.min.css", "select2-bootstrap4.min.css")
}

SELECT2_MEDIA_JS = (("https://cdn.jsdelivr.net/npm/select2@4.1.0-beta.1/dist/js/select2.min.js"),)


class ProductGenericFilterForm(BaseForm):
    """A generic form used for filtering products."""

    name = forms.CharField(label=_("Name"), required=False, widget=inline_textinput(_("Name")))
    vendor = forms.CharField(label=_("Vendor"), required=False, widget=inline_textinput(_("Vendor")))
    subcategories = LaxMultipleChoiceField(label=_("Subcategories"), required=False)
    description = forms.CharField(label=_("Description"), required=False, widget=inline_textinput(_("Description")))
    valid_at = forms.DateTimeField(
        label=_("Valid at"), required=False, widget=IsoDateTimePickerInput, initial=timezone.now
    )
    is_store = forms.BooleanField(label=_("Is store-specific"), required=False)


class ProductFilterForm(ProductGenericFilterForm):
    """A form used for filtering products."""

    extra_metadata_raw = forms.CharField(label=_("Properties"), required=False)  # Takes JSON from ExtraMetadataEditor
    is_group = forms.BooleanField(label=_("Is in group"), required=False)

    class Media:
        css = SELECT2_MEDIA_CSS
        js = SELECT2_MEDIA_JS


class ProductGroupFilterForm(ProductGenericFilterForm):
    """A form used for filtering product groups."""

    pass


class VendorFilterForm(BaseForm):
    """A form used for filtering vendors."""

    name = forms.CharField(label=_("Name"), required=False, widget=inline_textinput(_("Name")))
    valid_at = forms.DateTimeField(
        label=_("Valid at"), required=False, widget=IsoDateTimePickerInput, initial=timezone.now
    )
    is_store = forms.BooleanField(label=_("Is store-specific"), required=False)


class LocalProductOverrideForm(BaseModelForm):
    """A form used for editing local overrides."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=True, widget=IsoDateTimePickerInput)
    date_ended = forms.DateTimeField(label=_("Valid until"), required=False, widget=IsoDateTimePickerInput)

    class Meta:
        model = LocalProductOverride
        fields = ["available", "price", "note", "date_started", "date_ended"]


class LocalProductOverrideDatesForm(BaseForm):
    """A form used for editing local override dates."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=True, widget=IsoDateTimePickerInput)
    date_ended = forms.DateTimeField(label=_("Valid until"), required=False, widget=IsoDateTimePickerInput)


class ProductAddEditBaseForm(BaseModelForm):
    """A form used for adding or editing products."""

    class Meta:
        model = Product
        fields = [
            "name",
            "vendor",
            "description",
            "subcategory",
            "photo",
            "price",
            "amount",
            "amount_unit",
            "any_amount",
            "store",  # Shown only to global managers
            "extra_metadata_raw",
            "group",
            "date_started",
            "date_ended",
        ]
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control", "placeholder": _("Amount")}),
            "amount_unit": forms.Select(attrs={"class": "form-control"}),
        }

    class Media:
        css = SELECT2_MEDIA_CSS
        js = SELECT2_MEDIA_JS


class ProductAddForm(ProductAddEditBaseForm):
    """A form used for adding products."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=False, widget=IsoDateTimePickerInput)
    date_ended = forms.DateTimeField(label=_("Valid until"), required=False, widget=IsoDateTimePickerInput)


class ProductEditForm(ProductAddEditBaseForm):
    """A form used for editing products."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=True, widget=IsoDateTimePickerInput)
    date_ended = forms.DateTimeField(label=_("Valid until"), required=False, widget=IsoDateTimePickerInput)


class ProductGroupAddEditForm(BaseModelForm):
    """A form used for adding or editing product groups."""

    class Meta:
        model = ProductGroup
        fields = [
            "name",
            "vendor",
            "description",
            "subcategory",
            "photo",
            "store",  # Shown only to global managers
            "date_started",  # date_ended is hidden, and only set when deleting a group
        ]


class ProductGroupAddForm(ProductGroupAddEditForm):
    """A form used for adding product groups."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=False, widget=IsoDateTimePickerInput)


class ProductGroupEditForm(ProductGroupAddEditForm):
    """A form used for editing product groups."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=True, widget=IsoDateTimePickerInput)


class CategoryForm(BaseModelForm):
    """A form used for editing categories."""

    class Meta:
        model = Category
        fields = ["name", "description", "visible"]


class SubcategoryForm(BaseModelForm):
    """A form used for editing subcctegories."""

    class Meta:
        model = Subcategory
        fields = ["name", "description", "visible", "parent"]


class GenericSubaisleForm(BaseModelForm):
    """A form for editing generic subaisles."""

    class Meta:
        model = GenericSubaisle
        fields = ["name", "description", "subcategories"]


class StandardMetaFieldForm(BaseModelForm):
    """A form for editing standard properties."""

    expected_units = forms.TypedChoiceField(
        label=_("Expected units"),
        widget=forms.RadioSelect,
        choices=ms_products.constants.META_UNITS_CHOICES,
        required=True,
    )
    expected_units_custom_text = forms.CharField(
        label=_("Custom unit names"),
        required=False,
        widget=forms.Textarea,
        help_text=_("Specify units available to the users, one per line."),
    )

    class Meta:
        model = StandardMetaField
        fields = ["name", "expected_units", "subcategories_required", "subcategories_recommended"]


class VendorAddEditBaseForm(BaseModelForm):
    """A form used for adding or editing vendors."""

    class Meta:
        model = Vendor
        fields = ["name", "logo", "website", "description", "store", "date_started", "date_ended"]


class VendorAddForm(VendorAddEditBaseForm):
    """A form used for adding vendors."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=False, widget=IsoDateTimePickerInput)
    date_ended = forms.DateTimeField(label=_("Valid until"), required=False, widget=IsoDateTimePickerInput)


class VendorEditForm(VendorAddEditBaseForm):
    """A form used for editing vendors."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=True, widget=IsoDateTimePickerInput)
    date_ended = forms.DateTimeField(label=_("Valid until"), required=False, widget=IsoDateTimePickerInput)
