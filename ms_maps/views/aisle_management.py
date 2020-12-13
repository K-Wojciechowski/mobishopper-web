"""Aisle management views for ms_maps."""
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from ms_baseline.permission_helpers import permissions_required_maps
from ms_baseline.utils import render, render_delete
from ms_maps import forms
from ms_maps.models import Aisle, Subaisle
from ms_maps.utils import build_aisles_structure
from ms_maps.views.aisle_dual_forms import GenericFormStatus, generic_add, generic_edit


@permissions_required_maps
def aisles_list(request):
    """Show a list of aisles."""
    show_all = "all" in request.GET
    aisles = build_aisles_structure(request.ms_store, visible_only=not show_all, include_counts=True)
    context = {"aisles": aisles, "show_all": show_all}
    return render(request, "mobishopper/maps/aisles_list.html", _("Aisles"), context)


@permissions_required_maps
def aisles_add(request):
    """Add an aisle."""
    status, form, _instance, extras = generic_add(request, forms.AisleAddEditForm, show_success_message=True)
    if status == GenericFormStatus.success:
        return redirect("ms_maps:aisles_list")
    context = {"form": form, "form_name": "aisle"}
    context.update(extras)
    return render(request, "mobishopper/maps/aisle_form_holder.html", _("Add aisle"), context)


@permissions_required_maps
def aisles_edit(request, id):
    """Edit an aisle."""
    instance = get_object_or_404(Aisle, id=id)
    status, form, instance, extras = generic_edit(request, instance, forms.AisleAddEditForm, show_success_message=True)
    context = {"form": form, "form_name": "aisle"}
    context.update(extras)
    return render(request, "mobishopper/maps/aisle_form_holder.html", _("Edit aisle {0}").format(instance), context)


@permissions_required_maps
def subaisles_add(request):
    """Add a subaisle."""
    status, form, _instance, extras = generic_add(request, forms.SubaisleAddEditForm, show_success_message=True)
    if status == GenericFormStatus.success:
        return redirect("ms_maps:aisles_list")
    context = {"form": form, "form_name": "subaisle"}
    context.update(extras)
    return render(request, "mobishopper/maps/aisle_form_holder.html", _("Add subaisle"), context)


@permissions_required_maps
def subaisles_edit(request, id):
    """Edit a subaisle."""
    instance = get_object_or_404(Subaisle, id=id)
    status, form, instance, extras = generic_edit(
        request, instance, forms.SubaisleAddEditForm, show_success_message=True
    )
    context = {"form": form, "form_name": "subaisle"}
    context.update(extras)
    return render(request, "mobishopper/maps/aisle_form_holder.html", _("Edit subaisle {0}").format(instance), context)


@permissions_required_maps
def aisles_delete(request, id):
    """Delete an aisle."""
    instance = get_object_or_404(Aisle, id=id)
    return render_delete(
        request,
        instance,
        reverse("ms_maps:aisles_list"),
        reverse("ms_maps:aisles_edit", args=(id,)),
        _(
            "Maps that use subaisles of this aisle will be modified. The tiles will be replaced with Product shelf tiles."
        ),
    )


@permissions_required_maps
def subaisles_delete(request, id):
    """Delete a subaisle."""
    instance = get_object_or_404(Subaisle, id=id)
    return render_delete(
        request,
        instance,
        reverse("ms_maps:aisles_list"),
        reverse("ms_maps:subaisles_edit", args=(id,)),
        _("Maps that use this subaisle will be modified. The tiles will be replaced with Product shelf tiles."),
    )
