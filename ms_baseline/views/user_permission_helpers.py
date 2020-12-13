"""Permission helpers for ms_baseline views."""
from django.contrib import messages
from django.utils.translation import gettext as _

from ms_baseline import constants
from ms_baseline.models import MsUser, Store, UserStorePermission


def _remove_local_from_store(user: MsUser, store: Store) -> bool:
    """Remove local permissions of a user from the given store.

    If this is their only store, revoke access to management panel as well.

    :return: True if can access panel, false otherwise.
    :raise: UserStorePermission.DoesNotExist
    """
    UserStorePermission.objects.get(user=user, store=store).delete()
    usps = UserStorePermission.objects.filter(user=user)
    if not usps:
        user.is_manager = False
        user.save()
        return False
    return True


def _chtype_global(request, user: MsUser, form_data: dict):
    """Change user type in a global context."""
    if user == request.user and form_data["action"] != "full_manager":
        return messages.ERROR, _("Cannot change your own permissions with this panel."), True

    if form_data["action"] == "remove_all":
        user.is_manager = False
        user.is_global_manager = False
        for gp in constants.GLOBAL_PERMISSIONS:
            setattr(user, gp, False)
        user.save()
        UserStorePermission.objects.filter(user=user).delete()
        return messages.SUCCESS, _("All permissions removed."), True
    elif form_data["action"] == "local_manager":
        user.is_manager = True
        user.is_global_manager = False
        for gp in constants.GLOBAL_PERMISSIONS:
            setattr(user, gp, False)
        user.save()
        return messages.SUCCESS, _("Permission level set to local manager."), True
    elif form_data["action"] == "global_manager":
        user.is_manager = False
        user.is_global_manager = True
        for gp in constants.GLOBAL_PERMISSIONS:
            setattr(user, gp, gp in form_data["access"])
        user.save()
        UserStorePermission.objects.filter(user=user).delete()
        return messages.SUCCESS, _("Permission level set to global manager."), True
    elif form_data["action"] == "full_manager":
        user.is_manager = True
        user.is_global_manager = True
        for gp in constants.GLOBAL_PERMISSIONS:
            setattr(user, gp, gp in form_data["access"])
        user.save()
        return messages.SUCCESS, _("Permission level set to full manager."), True


def _chtype_local(request, user: MsUser, form_data: dict):
    """Change user type in a local context."""
    if user == request.user and form_data["action"] == "remove_all":
        return messages.ERROR, _("Cannot remove your own permissions."), True
    if form_data["action"] == "remove_all":
        can_access_admin = _remove_local_from_store(user, request.ms_store)
        if not can_access_admin:
            return messages.SUCCESS, _("All permissions removed."), False
        else:
            return (
                messages.SUCCESS,
                _("Local permissions removed, user is still a manager of a different store."),
                False,
            )
    elif form_data["action"] == "local_manager":
        user.is_manager = True
        user.save()
        try:
            usp = UserStorePermission.objects.get(user=user, store=request.ms_store)
        except UserStorePermission.DoesNotExist:
            usp = UserStorePermission(user=user, store=request.ms_store)
        for lp in constants.LOCAL_PERMISSIONS:
            setattr(usp, lp, lp in form_data["access"])
        usp.save()

        return messages.SUCCESS, _("Permission level set to local manager."), True
