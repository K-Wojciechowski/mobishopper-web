"""Dual form views for ms_maps."""
import enum
import typing

from ms_baseline.permission_helpers import PermissionDenied
from ms_maps import forms
from ms_maps.models import Aisle, Subaisle


class GenericFormStatus(enum.Enum):
    """Status of a generic form."""

    failure = 0
    success = 1
    show_form = 2


FormType = typing.Union[forms.AisleAddEditForm, forms.SubaisleAddEditForm]
InstanceType = typing.Union[Aisle, Subaisle]
ResultType = typing.Tuple[GenericFormStatus, FormType, typing.Optional[InstanceType], typing.Dict[str, typing.Any]]


def generic_add(request, form_cls: typing.Type[FormType], *, show_success_message: bool = False) -> ResultType:
    """Handle the generic aisle addition form."""
    instance: typing.Optional[InstanceType] = None
    if request.method == "POST":
        form: FormType = form_cls(request.POST)
        if form.is_valid():
            instance: InstanceType = form.save(commit=False)
            if isinstance(instance, Subaisle):
                instance.update_from_generic()
            instance.user = request.user
            instance.store = request.ms_store
            if show_success_message:
                success = instance.save_with_message(request)
            else:
                success = instance.save_with_error_message(request)
            form.save_m2m()
        else:
            success = False
        status = GenericFormStatus.success if success else GenericFormStatus.show_form
    else:
        form = form_cls()
        status = GenericFormStatus.show_form
    return status, form, instance, {"copy_global": None}


def generic_edit(
    request, instance: InstanceType, form_cls: typing.Type[FormType], *, show_success_message: bool = False
) -> ResultType:
    """Handle the generic aisle editing form."""
    if request.ms_store != instance.store:
        raise PermissionDenied()
    if request.method == "POST":
        _subaisle_generic = False
        if isinstance(instance, Subaisle):
            _subaisle_generic = request.POST.get("subaisle_form_copy_global") == "yes"
            form: FormType = form_cls(request.POST, instance=instance, _subaisle_generic=_subaisle_generic)
        else:
            form: FormType = form_cls(request.POST, instance=instance)
        if form.is_valid():
            instance: InstanceType = form.save(commit=False)
            if isinstance(instance, Subaisle):
                if _subaisle_generic:
                    instance.update_from_generic()
                else:
                    instance.generic_subaisle = None
            instance.user = request.user
            instance.store = request.ms_store
            success = instance.save_with_message(request)
            form.save_m2m()
        else:
            success = False
        status = GenericFormStatus.success if success else GenericFormStatus.show_form
    else:
        form = form_cls(instance=instance)
        status = GenericFormStatus.show_form

    if isinstance(instance, Subaisle):
        copy_global = bool(instance.generic_subaisle)
    else:
        copy_global = None

    return status, form, instance, {"copy_global": copy_global}
