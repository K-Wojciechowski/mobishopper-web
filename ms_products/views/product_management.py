"""Product management views."""
import logging
import typing

import django.utils.timezone
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from ms_baseline import vue_models
from ms_baseline.models import UserStorePermission
from ms_baseline.permission_helpers import (
    PermissionDenied,
    editable_in_store_context,
    permissions_required_products,
    permissions_required_products_local,
    permissions_required_products_readonly,
)
from ms_baseline.utils import (
    filter_in_effect,
    filter_in_effect_this_store_deals_m2m,
    filter_this_store,
    paginate,
    render,
)
from ms_deals.models import Coupon, Deal
from ms_products import forms
from ms_products.models import LocalProductOverride, Product
from ms_products.views.utils import get_global_upcoming_recent, get_local_upcoming_recent, handle_product_filters

logger = logging.getLogger("ms_products.views.product_management")


@permissions_required_products_readonly
def products_overview(request):
    """Show the products overview."""
    now = django.utils.timezone.now()
    context = {"products_global_count": Product.objects.filter(filter_in_effect(now)).filter(store=None).count()}
    context.update(get_global_upcoming_recent(now))

    context["products_global_upcoming_count"] = context["products_global_upcoming"].count()
    context["products_global_recent_count"] = context["products_global_recent"].count()

    if request.ms_store is not None:
        context.update(get_local_upcoming_recent(request, now))
        context["products_local_count"] = (
            Product.objects.filter(filter_in_effect(now)).filter(filter_this_store(request)).count()
        )
        context["products_local_upcoming_count"] = context["products_local_upcoming"].count()
        context["products_local_recent_count"] = context["products_local_recent"].count()

        context["products_recent"] = context["products_local_recent"]
        context["products_upcoming"] = context["products_local_upcoming"]
    else:
        context["products_recent"] = context["products_global_recent"]
        context["products_upcoming"] = context["products_global_upcoming"]

    context["products_recent"] = context["products_recent"].select_related("group", "vendor")
    context["products_upcoming"] = context["products_upcoming"].select_related("group", "vendor")

    return render(request, "mobishopper/products/products_overview.html", _("Products overview"), context)


@permissions_required_products_readonly
def products_recent_upcoming(request):
    """Show products with recent and upcoming changes."""
    now = django.utils.timezone.now()
    context = {}

    if request.ms_store is not None:
        context.update(get_local_upcoming_recent(request, now))
        context["products_recent"] = context["products_local_recent"]
        context["products_upcoming"] = context["products_local_upcoming"]
    else:
        context.update(get_global_upcoming_recent(now))
        context["products_recent"] = context["products_global_recent"]
        context["products_upcoming"] = context["products_global_upcoming"]

    context["products_recent"] = context["products_recent"].select_related("group", "vendor")
    context["products_upcoming"] = context["products_upcoming"].select_related("group", "vendor")

    return render(request, "mobishopper/products/products_recent_upcoming.html", _("Recent and upcoming"), context)


@permissions_required_products_readonly
def products_show_edit(request, id: int):
    """Show or edit a product."""
    product: Product = get_object_or_404(
        Product.objects.select_related("vendor", "group", "store", "subcategory", "subcategory__parent"), id=id
    )
    product_override: typing.Optional[LocalProductOverride] = None
    if request.ms_store is None:
        _show_editing = request.user.can_manage_global_products
        show_deals = request.user.can_manage_global_deals
        deals = Deal.objects.filter(filter_in_effect()).filter(product=product)
        coupons = Coupon.objects.filter(filter_in_effect()).filter(product=product)
    else:
        usp: UserStorePermission = request.ms_store_permission
        if not any([usp.can_manage_products, usp.can_manage_deals, usp.can_manage_maps]):
            raise PermissionDenied()
        _show_editing = usp.can_manage_products
        show_deals = usp.can_manage_deals
        deals = Deal.objects.filter(filter_in_effect_this_store_deals_m2m(request)).filter(product=product)
        coupons = Coupon.objects.filter(filter_in_effect_this_store_deals_m2m(request)).filter(product=product)
        try:
            product_override = LocalProductOverride.objects.filter(filter_in_effect() & filter_this_store(request)).get(
                product=product
            )
        except LocalProductOverride.DoesNotExist:
            pass

    _show_editing = _show_editing and not product.replaced_by
    show_local_override = _show_editing and request.ms_store is not None and product.store is None
    show_editing_pane = _show_editing and editable_in_store_context(request, product)

    replacement_of: typing.Optional[Product] = None
    try:
        replacement_of = Product.objects.get(replaced_by=product)
    except Product.DoesNotExist:
        pass

    context = {
        "product": product,
        "product_override": product_override,
        "product_replacement_of": replacement_of,
        "deals": deals,
        "coupons": coupons,
        "show_local_override": show_local_override,
        "show_editing_pane": show_editing_pane,
        "show_deals": show_deals,
    }

    # Local override editing
    if show_local_override:
        local_override_form = forms.LocalProductOverrideForm()
        local_override_dates_form = forms.LocalProductOverrideDatesForm()

        if request.method == "POST" and request.POST["action"] == "local_override_dates":
            local_override_dates_form = forms.LocalProductOverrideDatesForm(request.POST)
            if local_override_dates_form.is_valid():
                product_override.date_started = local_override_dates_form.cleaned_data["date_started"]
                product_override.date_ended = local_override_dates_form.cleaned_data["date_ended"]
                product_override.save_with_message(request)

        elif request.method == "POST" and request.POST["action"] == "local_override":
            local_override_form = forms.LocalProductOverrideForm(request.POST)
            if local_override_form.is_valid():
                new_override = local_override_form.save(commit=False)
                new_override.user = request.user
                new_override.store = request.ms_store
                new_override.product = product
                success = True
                if product_override is not None and (
                    product_override.date_ended is None or product_override.date_ended > new_override.date_started
                ):
                    product_override.date_ended = new_override.date_started
                    success = product_override.save_with_error_message(request)
                if success:
                    new_override.save_with_message(request)

        elif product_override:
            product_override: LocalProductOverride
            local_override_dates_form = forms.LocalProductOverrideDatesForm(
                {"date_started": product_override.date_started, "date_ended": product_override.date_ended}
            )

        context["local_override_form"] = local_override_form
        context["local_override_dates_form"] = local_override_dates_form

    if show_editing_pane:
        extra_metadata_raw_init = product.extra_metadata_raw
        if request.method == "POST" and request.POST["action"] == "edit":
            extra_metadata_raw_init = request.POST.get("extra_metadata_raw")
            old_product = Product.objects.get(id=product.id)
            edit_form = forms.ProductEditForm(request.POST, request.FILES, instance=product)
            if edit_form.is_valid():
                new_product: Product = edit_form.save(commit=False)
                new_product.id = None
                new_product.pk = None
                new_product.user = request.user
                if request.ms_store is not None:
                    new_product.store = request.ms_store
                new_product.save_as_replacement(request, old_product)
                return redirect(new_product.get_absolute_url())
        else:
            edit_form = forms.ProductEditForm(instance=product)
            now = django.utils.timezone.now()
            if product.date_ended and product.date_ended >= now:
                edit_form.initial["date_started"] = product.date_ended
            else:
                edit_form.initial["date_started"] = now
            edit_form.initial["date_ended"] = None

        vendor_name = group_name = ""
        vendor_initial = []
        group_initial = []
        if product.vendor:
            vendor_initial = [
                vue_models.ModalItem(
                    id=product.vendor.id, name=product.vendor.name, details_url=product.vendor.get_absolute_url()
                )
            ]
            vendor_name = product.vendor.name
        if product.group:
            group_initial = [
                vue_models.ModalItem(
                    id=product.group.id, name=product.group.name, details_url=product.group.get_absolute_url()
                )
            ]
            group_name = product.group.name

        vue_apps = [
            vue_models.AppDataMIS(
                APP_TAG="#product-vendor",
                misApiEndpoint=reverse("ms_products_api:vendors_modal"),
                misTitle=_("Choose a vendor"),
                misItemName=_("Vendor"),
                misModalId="product-vendor-modal",
                misInputName="vendor",
                misRequired=True,
                misInitialSelection=vendor_initial,
            ),
            vue_models.AppDataMIS(
                APP_TAG="#product-group",
                misApiEndpoint=reverse("ms_products_api:groups_modal"),
                misTitle=_("Choose a product group"),
                misItemName=_("Group"),
                misModalId="product-group-modal",
                misInputName="group",
                misRequired=False,
                misInitialSelection=group_initial,
            ),
            vue_models.AppDataEME(APP_TAG="#product-extra-metadata", emeInitialData=extra_metadata_raw_init),
        ]

        context["edit_form"] = edit_form
        context["vue_apps_json"] = vue_models.get_json(vue_apps)
        context["vendor_name"] = vendor_name
        context["group_name"] = group_name

    return render(request, "mobishopper/products/products_show_edit.html", product.name, context)


@permissions_required_products
def products_add(request):
    """Add a product."""
    if request.method == "POST":
        form = forms.ProductAddForm(request.POST, request.FILES)
        if form.is_valid():
            new_product: Product = form.save(commit=False)
            new_product.user = request.user
            if request.ms_store is not None:
                new_product.store = request.ms_store
            new_product.save_with_message(request)
            return redirect(new_product.get_absolute_url())
    else:
        form = forms.ProductAddForm()
        form.initial["date_started"] = django.utils.timezone.now()

    vue_apps = [
        vue_models.AppDataMIS(
            APP_TAG="#product-vendor",
            misApiEndpoint=reverse("ms_products_api:vendors_modal"),
            misTitle=_("Choose a vendor"),
            misItemName=_("Vendor"),
            misModalId="product-vendor-modal",
            misInputName="vendor",
            misRequired=True,
        ),
        vue_models.AppDataMIS(
            APP_TAG="#product-group",
            misApiEndpoint=reverse("ms_products_api:groups_modal"),
            misTitle=_("Choose a product group"),
            misItemName=_("Group"),
            misModalId="product-group-modal",
            misInputName="group",
            misRequired=False,
        ),
        vue_models.AppDataEME(APP_TAG="#product-extra-metadata"),
    ]

    context = {"form": form, "vue_apps_json": vue_models.get_json(vue_apps)}

    return render(request, "mobishopper/products/products_add.html", _("Add a product"), context)


@permissions_required_products_readonly
def products_list(request):
    """Show a list of products."""
    form, filtering_error, products, order = handle_product_filters(request, forms.ProductFilterForm, Product)
    products = products.select_related("vendor")
    can_add = (request.ms_store is None and request.user.can_manage_global_products) or (
        request.ms_store is not None and request.ms_store_permission.can_manage_products
    )

    paginator, page = paginate(products, request)
    context = {
        "search_form": form,
        "paginator": paginator,
        "products": page,
        "order": order,
        "filtering_error": filtering_error,
        "add_button_dest": reverse("ms_products:add") if can_add else None,
    }
    return render(request, "mobishopper/products/products_list.html", _("Products"), context)


@permissions_required_products_readonly
def products_search(request):
    """Show full product search page."""
    form = forms.ProductFilterForm()
    vue_apps = [vue_models.AppDataEME(APP_TAG="#search-extra-metadata", emeHighlightCustom=False)]
    context = {
        "form": form,
        "vue_apps_json": vue_models.get_json(vue_apps),
        "show_product_only_fields": True,
        "action_url": reverse("ms_products:list"),
    }
    return render(request, "mobishopper/products/products_search.html", _("Search"), context)


@permissions_required_products_local
def products_local_overrides(request):
    """Show products with local overrides."""
    overrides = LocalProductOverride.objects.filter(store=request.ms_store)
    show_all = "all" in request.GET
    if not show_all:
        overrides = overrides.filter(filter_in_effect())
    paginator, page = paginate(overrides, request)
    context = {"paginator": paginator, "overrides": page, "show_all": show_all}
    return render(request, "mobishopper/products/products_local_overrides.html", _("Local overrides"), context)
