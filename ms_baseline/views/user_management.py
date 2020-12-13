"""User management views."""
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.crypto import constant_time_compare
from django.utils.html import format_html
from django.utils.translation import gettext as _

from ms_baseline import constants, forms
from ms_baseline.models import MsUser, UserStorePermission
from ms_baseline.permission_helpers import permissions_required_users
from ms_baseline.utils import paginate, render, render_delete
from ms_baseline.views.user_edit_helpers import _user_edit_save_local_permissions, _users_edit_global, _users_edit_local
from ms_baseline.views.user_permission_helpers import _chtype_global, _chtype_local


@permissions_required_users
def users_list(request):
    """Show a list of users."""
    search_form = forms.UserSearchForm(request.GET)
    base_filters = {}
    if search_form.is_valid():
        cd = search_form.cleaned_data.copy()
        show_managers_only = cd.pop("managers_only")
        for field_name, field_value in cd.items():
            if field_value.strip():
                base_filters[field_name + "__startswith"] = field_value.strip()
    else:
        show_managers_only = False

    if request.ms_store is None and show_managers_only:
        users = (
            MsUser.objects.filter(Q(is_manager=True) | Q(is_global_manager=True))
            .filter(**base_filters)
            .order_by("email")
        )
    elif not request.ms_store:
        users = MsUser.objects.filter(**base_filters).order_by("email")
    else:
        usps = UserStorePermission.objects.filter(store=request.ms_store)
        usp_filters = {"user__" + k: v for k, v in base_filters.items()}
        users = [u.user for u in usps.select_related("user").filter(**usp_filters).order_by("user__email")]
    paginator, page = paginate(users, request)
    context = {
        "paginator": paginator,
        "users": page,
        "sidebar": "ms_baseline_users",
        "current_app": "ms_baseline_users",
        "search_form": search_form,
        "add_button_dest": reverse("ms_baseline:users_add"),
    }

    return render(request, "mobishopper/users/users_list.html", _("Users"), context)


@permissions_required_users
def users_add(request):
    """Add a new user."""
    if request.ms_store is None:
        template = "mobishopper/users/users_edit_global.html"
        form_class = forms.UserGlobalAddForm
    else:
        template = "mobishopper/users/users_edit_local.html"
        form_class = forms.UserLocalAddForm

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            ret = _save_new_user(request, form)
            if ret:
                return ret
    else:
        form = form_class()
        if request.ms_store is not None:
            form.fields["is_manager"].initial = True

    return render(
        request,
        template,
        _("Add new user"),
        {"form": form, "sidebar": "ms_baseline_users", "current_app": "ms_baseline_users", "is_adding": True, "id": -1},
    )


@permissions_required_users
def users_edit(request, id):
    """Edit a user."""
    user = get_object_or_404(MsUser, id=id)
    if request.ms_store is None:
        return _users_edit_global(request, user)
    else:
        return _users_edit_local(request, user)


@permissions_required_users
def users_reset_password(request, id):
    """Reset a user’s password."""
    user = get_object_or_404(MsUser, id=id)
    if request.ms_store is not None:
        _usp = get_object_or_404(UserStorePermission, user=user)

    if request.method == "POST":
        form = forms.PasswordResetForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["new_password1"] != form.cleaned_data["new_password2"]:
                messages.error(request, _("Passwords do not match."))
            else:
                user.set_password(form.cleaned_data["new_password1"])
                user.save_with_error_message(request)
                messages.info(request, _("Password has been reset."))
                return redirect(reverse("ms_baseline:users_edit", args=(user.id,)))
    # Create form unconditionally to clean inputs
    form = forms.PasswordResetForm()
    return render(
        request,
        "mobishopper/users/users_reset_password.html",
        _("Reset password for {0}").format(user.get_full_name()),
        {"form": form, "sidebar": "ms_baseline_users", "current_app": "ms_baseline_users", "id": user.id},
    )


@permissions_required_users
def users_delete(request, id):
    """Delete a user."""
    user = get_object_or_404(MsUser, id=id)
    return render_delete(
        request, user, reverse("ms_baseline:users_list"), reverse("ms_baseline:users_edit", args=(id,))
    )


@permissions_required_users
def users_change_type(request):
    """Change type of a user."""
    if request.ms_store:
        template = "mobishopper/users/users_change_type_local.html"
        form_class = forms.ChangeLocalTypeForm
        callback = _chtype_local
    else:
        template = "mobishopper/users/users_change_type_global.html"
        form_class = forms.ChangeGlobalTypeForm
        callback = _chtype_global

    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            try:
                user = MsUser.objects.get(email=form.cleaned_data["email"])
            except MsUser.DoesNotExist:
                messages.info(request, _("User does not exist."))
            else:
                msg_type, msg_text, msg_add = callback(request, user, form.cleaned_data)
                if msg_add:
                    msg_text = format_html(
                        '{0} <a href="{1}">{2}</a>',
                        msg_text,
                        reverse("ms_baseline:users_edit", args=(user.id,)),
                        _("Edit profile"),
                    )
                messages.add_message(request, msg_type, msg_text)
    else:
        form = form_class()

    return render(
        request,
        template,
        _("Change user type and permissions"),
        {
            "form": form,
            "sidebar": "ms_baseline_users",
            "current_app": "ms_baseline_users",
        },
    )


def _save_new_user(request, form):
    """Save a new user."""
    if request.ms_store is None:
        data = {k: v for k, v in form.cleaned_data.items() if k in constants.ALL_USER_DATA}
        user = MsUser(**data)
        user.save_with_error_message(request)
        _user_edit_save_local_permissions(request, form, user)
    else:
        if not form.cleaned_data["is_manager"]:
            messages.error(request, _("You can only add local manager accounts. Customers can register in the app."))
            return
        data = {k: v for k, v in form.cleaned_data.items() if k in ["email", "first_name", "last_name", "is_manager"]}
        user = MsUser(**data)

    if not constant_time_compare(form.cleaned_data["new_password1"], form.cleaned_data["new_password2"]):
        messages.error(request, _("Passwords do not match."))
        return

    user.set_password(form.cleaned_data["new_password1"])
    success = user.save_with_error_message(request)
    if not success:
        return

    if request.ms_store is not None:
        usp_data = {k: v for k, v in form.cleaned_data.items() if k in constants.LOCAL_PERMISSIONS}
        usp = UserStorePermission(user=user, store=request.ms_store, **usp_data)
        usp.save_with_error_message(request)
    if success:
        messages.info(request, _("User has been added."))
        return redirect("ms_baseline:users_edit", user.id)
