"""Forms for ms_baseline."""
from django import forms
from django.utils.translation import gettext_lazy as _

from ms_baseline import constants
from ms_baseline.form_utils import BaseForm, BaseModelForm, inline_select, inline_textinput
from ms_baseline.models import CheckoutApiKey, Store


class ChangeLocalTypeForm(BaseForm):
    """Form used to change local user permissions."""

    email = forms.CharField(label=_("E-mail"))
    action = forms.ChoiceField(
        widget=forms.RadioSelect,
        required=True,
        label=_("Action"),
        choices=(("remove_all", _("Remove permissions")), ("local_manager", _("Mark as local manager"))),
    )
    access_local = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label=_("Local permissions"),
        required=True,
        choices=constants.LOCAL_PERMISSION_CHOICES,
    )


class ChangeGlobalTypeForm(BaseForm):
    """Form used to change global user permissions."""

    email = forms.EmailField(label=_("E-mail"))
    action = forms.ChoiceField(
        widget=forms.RadioSelect,
        required=True,
        label=_("Action"),
        choices=(
            ("remove_all", _("Remove all permissions")),
            ("local_manager", _("Mark as local manager")),
            ("global_manager", _("Mark as global manager")),
            ("full_manager", _("Mark as full manager")),
        ),
    )
    access = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        label=_("Global permissions"),
        required=True,
        choices=constants.GLOBAL_PERMISSION_CHOICES,
    )


class UserSearchForm(BaseForm):
    """Form used to search for users."""

    first_name = forms.CharField(label=_("First name"), required=False, widget=inline_textinput(_("First name")))
    last_name = forms.CharField(label=_("Last name"), required=False, widget=inline_textinput(_("Last name")))
    email = forms.EmailField(label=_("E-mail"), required=False, widget=inline_textinput(_("E-mail")))
    managers_only = forms.BooleanField(label=_("Show managers only"), required=False)


class UserLocalEditForm(BaseForm):
    """Form used to edit local users."""

    email = forms.EmailField(label=_("E-mail"), required=True)
    first_name = forms.CharField(label=_("First name"), required=True)
    last_name = forms.CharField(label=_("Last name"), required=True)
    is_manager = forms.BooleanField(label=_("Manages this store"), required=False)
    can_manage_products = forms.BooleanField(label=_("Can manage products"), required=False)
    can_manage_maps = forms.BooleanField(label=_("Can manage maps"), required=False)
    can_manage_deals = forms.BooleanField(label=_("Can manage deals"), required=False)
    can_manage_employees = forms.BooleanField(label=_("Can manage employees"), required=False)
    can_view_statistics = forms.BooleanField(label=_("Can view statistics"), required=False)


class UserGlobalEditForm(BaseForm):
    """Form used to edit global users."""

    email = forms.EmailField(label=_("E-mail"), required=True)
    first_name = forms.CharField(label=_("First name"), required=True)
    last_name = forms.CharField(label=_("Last name"), required=True)
    is_manager = forms.BooleanField(label=_("Local manager"), required=False)
    is_global_manager = forms.BooleanField(label=_("Global manager"), required=False)
    is_superuser = forms.BooleanField(label=_("System administrator"), required=False)
    can_manage_global_products = forms.BooleanField(label=_("Can manage global products"), required=False)
    can_manage_global_deals = forms.BooleanField(label=_("Can manage global deals"), required=False)
    can_view_global_statistics = forms.BooleanField(label=_("Can view global statistics"), required=False)
    can_manage_users = forms.BooleanField(label=_("Can manage users"), required=False)
    can_manage_stores = forms.BooleanField(label=_("Can manage stores"), required=False)
    local_permissions_json = forms.JSONField(required=False)


class PasswordResetForm(BaseForm):
    """Form used to reset passwords."""

    new_password1 = forms.CharField(label=_("New password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("Repeat password"), widget=forms.PasswordInput)


class UserLocalAddForm(UserLocalEditForm):
    """Form used to add local users."""

    new_password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("Repeat password"), widget=forms.PasswordInput)


class UserGlobalAddForm(UserGlobalEditForm):
    """Form used to add global users."""

    new_password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    new_password2 = forms.CharField(label=_("Repeat password"), widget=forms.PasswordInput)


class StoreSearchForm(BaseForm):
    """Form used to search for stores."""

    name = forms.CharField(label=_("Name"), required=False, widget=inline_textinput(_("Name")))
    city = forms.EmailField(label=_("City"), required=False, widget=inline_textinput(_("City")))
    visibility = forms.ChoiceField(
        choices=constants.STORE_VISIBILITY_CHOICES, label=_("Visibility"), widget=inline_select()
    )


class StoreAddEditForm(BaseModelForm):
    """Form used to add or edit stores."""

    class Meta:
        model = Store
        fields = ["name", "address", "city", "region_code", "hidden"]


class CheckoutApiKeyAddEditForm(BaseModelForm):
    """Form used to add or edit Checkout API Keys."""

    class Meta:
        model = CheckoutApiKey
        fields = ["name", "store", "is_active"]
