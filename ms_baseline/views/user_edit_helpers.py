"""Helpers for user editing."""

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from ms_baseline import constants, forms, vue_models
from ms_baseline.models import Store, UserStorePermission
from ms_baseline.permission_helpers import PermissionDenied
from ms_baseline.utils import render
from ms_baseline.views.user_permission_helpers import _remove_local_from_store


def _users_edit_local(request, user):
    """Edit a user in the local context."""
    try:
        usp = UserStorePermission.objects.get(store=request.ms_store, user=user)
    except UserStorePermission.DoesNotExist:
        raise PermissionDenied()

    if request.method == "POST":
        form = forms.UserLocalEditForm(request.POST)
        if form.is_valid():
            for user_key in ["email", "first_name", "last_name"]:
                setattr(user, user_key, form.cleaned_data[user_key])
            user.save_with_error_message(request)

            if not form.cleaned_data["is_manager"]:
                if request.user == user:
                    messages.error(request, _("You cannot remove yourself from a store."))
                else:
                    _remove_local_from_store(user, request.ms_store)
                    return redirect(reverse("ms_baseline:users_list"))
            else:
                for usp_key in constants.LOCAL_PERMISSIONS:
                    setattr(usp, usp_key, form.cleaned_data[usp_key])
                if request.user == user and not form.cleaned_data["can_manage_employees"]:
                    messages.error(
                        request, _("You cannot remove the permission to manage employees from your own account.")
                    )
                    form.cleaned_data["can_manage_employees"] = True
                usp.save_with_message(request)
                messages.info(request, _("Changes saved."))
            # Special-casing for current user
            if request.user.id == user.id:
                return redirect(request.get_full_path())
    else:
        form_data = {"is_manager": True}
        for user_key in constants.LOCAL_USER_DATA:
            form_data[user_key] = getattr(user, user_key)
        for usp_key in constants.LOCAL_PERMISSIONS:
            form_data[usp_key] = getattr(usp, usp_key)
        form = forms.UserLocalEditForm(form_data)

    return render(
        request,
        "mobishopper/users/users_edit_local.html",
        _("Edit user {0}").format(user.get_full_name()),
        {"form": form, "sidebar": "ms_baseline_users", "is_adding": False, "id": user.id},
    )


def _users_edit_global(request, user):
    """Edit a user in the global context."""
    usps = UserStorePermission.objects.filter(user=user)
    if request.method == "POST":
        form = forms.UserGlobalEditForm(request.POST)
        if form.is_valid():
            for user_key in constants.ALL_USER_DATA:
                setattr(user, user_key, form.cleaned_data[user_key])
            user.save_with_error_message(request)
        _user_edit_save_local_permissions(request, form, user)
        messages.info(request, _("Changes saved."))
        # Special-casing for current user
        if request.user.id == user.id:
            return redirect(request.get_full_path())
    else:
        form_data = {}
        for user_key in constants.ALL_USER_DATA:
            form_data[user_key] = getattr(user, user_key)
        form = forms.UserGlobalEditForm(form_data)

    vue_apps = [
        vue_models.AppDataLPT(
            APP_TAG="#vue-app-local-permissions",
            lpTableTitles=[(key, str(title)) for key, title in constants.LOCAL_PERMISSION_TABLE_TITLES],
            lpEntries=[vue_models.LocalPermissionEntry.from_db(usp) for usp in usps],
        )
    ]
    vue_apps_json = vue_models.get_json(vue_apps)

    return render(
        request,
        "mobishopper/users/users_edit_global.html",
        _("Edit user {0}").format(user.get_full_name()),
        {
            "form": form,
            "sidebar": "ms_baseline_users",
            "is_adding": False,
            "id": user.id,
            "vue_apps_json": vue_apps_json,
        },
    )


def _user_edit_save_local_permissions(request, form, user):
    """Save local permissions from JSON when editing a user in the global context."""
    current_usps = UserStorePermission.objects.filter(user=user)
    usps_by_id = {usp.store.id: usp for usp in current_usps}
    existing_stores = set(usps_by_id)
    seen_stores = set()
    new_data = form.cleaned_data["local_permissions_json"] or []
    for store_data in new_data:
        store_id = store_data["id"]
        seen_stores.add(store_id)
        if store_id in usps_by_id:
            usp = usps_by_id[store_id]
        else:
            usp = UserStorePermission(user=user, store=Store.objects.get(id=store_id))
        for k in constants.LOCAL_PERMISSIONS:
            setattr(usp, k, store_data.get(k, False))
        usp.save_with_error_message(request)

    for deleted_store in existing_stores - seen_stores:
        usps_by_id[deleted_store].delete()
