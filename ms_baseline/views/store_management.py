"""Store management views."""
import operator

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from ms_baseline import forms
from ms_baseline.models import CheckoutApiKey, Store, UserStorePermission
from ms_baseline.permission_helpers import (
    permissions_required,
    permissions_required_custom,
    permissions_required_stores,
)
from ms_baseline.utils import paginate, render, render_delete


@permissions_required_stores
def stores_list(request):
    """List available stores."""
    search_form = forms.StoreSearchForm(request.GET)
    base_filters = {}
    if search_form.is_valid():
        for field_name in ["name", "city"]:
            field_value = search_form.cleaned_data.get(field_name, "")
            if field_value.strip():
                base_filters[field_name + "__startswith"] = field_value.strip()
        if search_form.cleaned_data["visibility"] == "hidden":
            base_filters["hidden"] = True
        elif search_form.cleaned_data["visibility"] == "visible":
            base_filters["hidden"] = False
    else:
        base_filters["hidden"] = False

    stores = Store.objects.filter(**base_filters).order_by("name")
    paginator, page = paginate(stores, request)

    context = {
        "paginator": paginator,
        "stores": page,
        "current_app": "ms_baseline_stores",
        "sidebar": "ms_baseline_stores",
        "search_form": search_form,
        "add_button_dest": reverse("ms_baseline:stores_add"),
    }

    return render(request, "mobishopper/stores/stores_list.html", _("Stores"), context)


@permissions_required_stores
def stores_add(request):
    """Add a new store."""
    if request.method == "POST":
        form = forms.StoreAddEditForm(request.POST)
        if form.is_valid():
            store = form.save_with_message(request)
            return redirect(reverse("ms_baseline:stores_edit", args=(store.id,)))
    else:
        form = forms.StoreAddEditForm()
    return render(
        request,
        "mobishopper/stores/stores_edit.html",
        _("Add store"),
        {"form": form, "is_adding": True, "current_app": "ms_baseline_stores", "sidebar": "ms_baseline_stores"},
    )


@permissions_required_stores
def stores_edit(request, id):
    """Edit a store."""
    store = get_object_or_404(Store, id=id)
    if request.method == "POST":
        form = forms.StoreAddEditForm(request.POST, instance=store)
        if form.is_valid():
            form.save_with_message(request)
    else:
        form = forms.StoreAddEditForm(instance=store)
    return render(
        request,
        "mobishopper/stores/stores_edit.html",
        _("Edit store {}").format(store),
        {
            "form": form,
            "id": store.id,
            "is_adding": False,
            "current_app": "ms_baseline_stores",
            "sidebar": "ms_baseline_stores",
        },
    )


@permissions_required_custom(lambda user, usp: user.is_superuser or (user.can_manage_users and user.can_manage_stores))
def stores_users(request, id):
    """Show a list of store employees."""
    store = get_object_or_404(Store, id=id)
    usps = UserStorePermission.objects.filter(store=store)
    users = sorted(set([usp.user for usp in usps]), key=operator.attrgetter("email"))
    return render(
        request,
        "mobishopper/stores/stores_users.html",
        _("Employees of store {}").format(store),
        {"users": users, "current_app": "ms_baseline_stores", "sidebar": "ms_baseline_stores"},
    )


@permissions_required(glob=["is_superuser"])
def stores_delete(request, id):
    """Delete a store."""
    obj = get_object_or_404(Store, id=id)
    return render_delete(
        request, obj, reverse("ms_baseline:stores_list"), reverse("ms_baseline:stores_edit", args=(id,))
    )


@permissions_required_stores
def checkout_api_keys_list(request):
    """List checkout API keys."""
    keys = CheckoutApiKey.objects.order_by("name")
    paginator, page = paginate(keys, request)

    context = {
        "paginator": paginator,
        "keys": page,
        "sidebar": "ms_baseline_stores",
        "current_app": "ms_baseline_stores",
        "add_button_dest": reverse("ms_baseline:checkout_api_keys_add"),
    }

    return render(request, "mobishopper/checkout_api_keys/checkout_api_keys_list.html", _("Checkout API keys"), context)


@permissions_required_stores
def checkout_api_keys_add(request):
    """Add a new API key."""
    if request.method == "POST":
        form = forms.CheckoutApiKeyAddEditForm(request.POST)
        if form.is_valid():
            key: CheckoutApiKey = form.save(commit=False)
            key.user = request.user
            key.save_with_message(request)
            request.session["show_checkout_api_key"] = str(key.key)
            return redirect(reverse("ms_baseline:checkout_api_keys_edit", args=(key.id,)))
    else:
        form = forms.CheckoutApiKeyAddEditForm()
    return render(
        request,
        "mobishopper/checkout_api_keys/checkout_api_keys_edit.html",
        _("Add checkout API key"),
        {
            "form": form,
            "is_adding": True,
            "sidebar": "ms_baseline_stores",
            "current_app": "ms_baseline_stores",
            "show_key": False,
        },
    )


@permissions_required_stores
def checkout_api_keys_edit(request, id):
    """Edit an API key."""
    key = get_object_or_404(CheckoutApiKey, id=id)
    shown_key = request.session.pop("show_checkout_api_key", None)
    if shown_key != str(key.key):
        shown_key = ""
    if request.method == "POST":
        form = forms.CheckoutApiKeyAddEditForm(request.POST, instance=key)
        if form.is_valid():
            key: CheckoutApiKey = form.save(commit=False)
            key.user = request.user
            key.save_with_message(request)
    else:
        form = forms.CheckoutApiKeyAddEditForm(instance=key)
    return render(
        request,
        "mobishopper/checkout_api_keys/checkout_api_keys_edit.html",
        _("Edit store {}").format(key),
        {
            "form": form,
            "id": key.id,
            "is_adding": False,
            "sidebar": "ms_baseline_stores",
            "current_app": "ms_baseline_stores",
            "shown_key": shown_key,
        },
    )


@permissions_required_stores
def checkout_api_keys_delete(request, id):
    """Delete an API key."""
    obj = get_object_or_404(CheckoutApiKey, id=id)
    return render_delete(
        request,
        obj,
        reverse("ms_baseline:checkout_api_keys_list"),
        reverse("ms_baseline:checkout_api_keys_edit", args=(id,)),
    )
