"""Forms for ms_maps."""
from django import forms
from django.utils.translation import gettext_lazy as _

from ms_baseline.form_utils import BaseForm, BaseModelForm, IsoDateTimePickerInput
from ms_maps.models import Aisle, Subaisle


class AisleAddEditForm(BaseModelForm):
    """A form used for adding or editing aisles."""

    class Meta:
        model = Aisle
        fields = ["code", "name", "description"]


class SubaisleAddEditForm(BaseModelForm):
    """A form used for adding or editing subaisles."""

    def __init__(self, *args, **kwargs):
        """Construct a SubaisleAddEditForm."""
        _subaisle_generic = None
        if "_subaisle_generic" in kwargs:
            kwargs.pop("_subaisle_generic")
        super().__init__(*args, **kwargs)
        # Override required to allow copying from generic subaisles
        if _subaisle_generic is True or _subaisle_generic is None:
            self.fields["name"].required = False
            self.fields["description"].required = False
            self.fields["subcategories"].required = False
        if _subaisle_generic is False or _subaisle_generic is None:
            self.fields["generic_subaisle"].required = False

    class Meta:
        model = Subaisle
        fields = [
            "code",
            "name",
            "description",
            "parent",
            "generic_subaisle",
            "subcategories",
        ]


class DatePickerPlaceholderForm(BaseForm):
    """A placeholder form used to configure bootstrap-datepicker inside a Vue app."""

    date_started = forms.DateTimeField(label=_("Valid from"), required=False, widget=IsoDateTimePickerInput)
