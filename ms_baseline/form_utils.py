"""Utilities for forms."""
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

IsoDatePickerInput = DatePickerInput(format="%Y-%m-%d")
IsoDateTimePickerInput = DateTimePickerInput(format="%Y-%m-%d %H:%M:%S")


class LaxMultipleChoiceField(forms.MultipleChoiceField):
    """A multiple choice field that is not displayed and that doesn’t validate choices."""

    hidden_widget = forms.MultipleHiddenInput
    widget = forms.MultipleHiddenInput
    default_error_messages = {"invalid_list": _("Enter a list of values.")}

    def validate(self, value):
        """Validate that the input is a list or tuple."""
        if self.required and not value:
            raise forms.ValidationError(self.error_messages["required"], code="required")


inline_textinput = lambda placeholder: forms.TextInput(attrs={"class": "form-control mr-2", "placeholder": placeholder})
inline_emailinput = lambda placeholder: forms.EmailInput(
    attrs={"class": "form-control mr-2", "placeholder": placeholder}
)
inline_select = lambda: forms.Select(attrs={"class": "custom-select mr-2"})


class BaseForm(forms.Form):
    """Base form for MobiShopper."""

    def save_with_message(self, request):
        """Save a form with a message."""
        # noinspection PyBroadException
        f = None
        try:
            f = self.save()
            messages.info(request, _("Changes saved."))
        except ValidationError as e:
            messages.error(request, _("Failed to save changes: {0}").format(e))
        except Exception:
            messages.error(request, _("Failed to save changes."))

        return f


class BaseModelForm(forms.ModelForm):
    """Base model form for MobiShopper."""

    def save_with_message(self, request):
        """Save a form with a message."""
        # noinspection PyBroadException
        f = None
        try:
            f = self.save()
            messages.info(request, _("Changes saved."))
        except ValidationError as e:
            messages.error(request, _("Failed to save changes: {0}").format(e))
        except Exception:
            messages.error(request, _("Failed to save changes."))

        return f
