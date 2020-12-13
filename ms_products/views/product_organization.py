"""Product organization views."""
import django.utils.timezone
from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from ms_baseline import vue_models
from ms_baseline.permission_helpers import (
    PermissionDenied,
    editable_in_store_context,
    permissions_required_products,
    permissions_required_products_global,
    permissions_required_products_readonly,
)
from ms_baseline.utils import filter_in_effect, paginate, render, render_delete, render_delete_get
from ms_products import forms
from ms_products.forms import GenericSubaisleForm
from ms_products.models import Category, GenericSubaisle, Product, ProductGroup, StandardMetaField, Subcategory, Vendor
from ms_products.views.utils import build_categories_structure, handle_product_filters


@permissions_required_products_global
def categories_list(request):
    """Show list of categories."""
    show_all = "all" in request.GET
    categories = build_categories_structure(visible_only=not show_all, include_counts=True)
    context = {"categories": categories, "show_all": show_all}
    return render(request, "mobishopper/products/categories_list.html", _("Categories"), context)


@permissions_required_products_global
def categories_add(request):
    """Add a new category."""
    if request.method == "POST":
        form = forms.CategoryForm(request.POST)
        if form.is_valid():
            res = form.save_with_message(request)
            if res:
                return redirect(reverse("ms_products:categories"))
    else:
        form = forms.CategoryForm()
    return render(request, "mobishopper/products/categories_add_edit.html", _("Add new category"), {"form": form})


@permissions_required_products_global
def categories_edit(request, id):
    """Edit a category."""
    cat = get_object_or_404(Category, id=id)
    subcategories = Subcategory.objects.filter(parent=cat)
    if request.method == "POST":
        form = forms.CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save_with_message(request)
    else:
        form = forms.CategoryForm(instance=cat)
    context = {"form": form, "subcategories": subcategories}
    return render(request, "mobishopper/products/categories_add_edit.html", _("Edit {}").format(cat), context)


@permissions_required_products_global
def subcategories_add(request):
    """Add a new subcategory."""
    if request.method == "POST":
        form = forms.SubcategoryForm(request.POST)
        if form.is_valid():
            res = form.save_with_message(request)
            if res:
                return redirect(reverse("ms_products:categories"))
    else:
        form = forms.SubcategoryForm()
    return render(request, "mobishopper/products/subcategories_add_edit.html", _("Add new subcategory"), {"form": form})


@permissions_required_products_global
def subcategories_edit(request, id):
    """Edit a subcategory."""
    subcat = get_object_or_404(Subcategory, id=id)
    recent_products = Product.objects.filter(subcategory=subcat).order_by("-date_started", "-date_added")[:10]
    if request.method == "POST":
        form = forms.SubcategoryForm(request.POST, instance=subcat)
        if form.is_valid():
            form.save_with_message(request)
    else:
        form = forms.SubcategoryForm(instance=subcat)
    context = {"form": form, "recent_products": recent_products, "id": subcat.id}
    return render(request, "mobishopper/products/subcategories_add_edit.html", _("Edit {}").format(subcat), context)


def _redirect_to_subcategory_search(subcategories):
    """Redirect to subcategory search page."""
    return redirect(reverse("ms_products:list") + "?" + "&".join(f"subcategories={sc.id}" for sc in subcategories))


@permissions_required_products_readonly
def categories_search(request, id):
    """Search for products in a category."""
    category = get_object_or_404(Category, id=id)
    subcategories = category.subcategory_set.all()
    return _redirect_to_subcategory_search(subcategories)


@permissions_required_products_readonly
def subcategories_search(request, id):
    """Search for products in a subcategory."""
    subcategory = get_object_or_404(Subcategory, id=id)
    return _redirect_to_subcategory_search([subcategory])


@permissions_required_products_global
def global_subaisles_list(request):
    """List global subaisles."""
    context = {
        "subaisles": GenericSubaisle.objects.all(),
        "add_button_dest": reverse("ms_products:global_subaisles_add"),
    }
    return render(request, "mobishopper/products/global_subaisles_list.html", _("Global subaisles"), context)


@permissions_required_products_global
def global_subaisles_add(request):
    """Add a global subaisle."""
    if request.method == "POST":
        form = GenericSubaisleForm(request.POST)
        res = form.save_with_message(request)
        if res:
            form.save_m2m()
            return redirect(reverse("ms_products:global_subaisles"))
    else:
        form = GenericSubaisleForm()
    context = {"form": form}
    return render(request, "mobishopper/products/global_subaisles_add_edit.html", _("Add global subaisle"), context)


@permissions_required_products_global
def global_subaisles_edit(request, id):
    """Edit a global subaisle."""
    subaisle = get_object_or_404(GenericSubaisle, id=id)
    if request.method == "POST":
        form = GenericSubaisleForm(request.POST, instance=subaisle)
        subaisle = form.save_with_message(request) or subaisle
    else:
        form = GenericSubaisleForm(instance=subaisle)
    context = {"form": form}
    return render(
        request,
        "mobishopper/products/global_subaisles_add_edit.html",
        _("Edit global subaisle {}").format(subaisle.name),
        context,
    )


@permissions_required_products_global
def global_subaisles_delete(request, id):
    """Delete a global subaisle."""
    subaisle = get_object_or_404(GenericSubaisle, id=id)
    destination = reverse("ms_products:global_subaisles")
    return render_delete(request, subaisle, destination, destination)


@permissions_required_products
def groups_list(request):
    """Show all product groups."""
    form, filtering_error, groups, order = handle_product_filters(request, forms.ProductGroupFilterForm, ProductGroup)

    groups = groups.annotate(size=Count("products", filter=filter_in_effect(prefix="products__")))

    paginator, page = paginate(groups, request)
    context = {
        "search_form": form,
        "paginator": paginator,
        "groups": page,
        "order": order,
        "show_order": True,
        "filtering_error": filtering_error,
        "add_button_dest": reverse("ms_products:groups_add"),
    }
    return render(request, "mobishopper/products/groups_list.html", _("Groups"), context)


@permissions_required_products
def groups_show(request, id):
    """Show a product group."""
    group = get_object_or_404(ProductGroup, id=id)
    products = Product.objects.filter(group=group)
    show_all = "all" in request.GET
    if not show_all:
        products = products.filter(filter_in_effect())
    return render(
        request,
        "mobishopper/products/groups_show.html",
        _("Products in group {0}").format(group.name),
        {"group": group, "products": products, "show_all": show_all},
    )


@permissions_required_products
def groups_add(request):
    """Add a product group."""
    if request.method == "POST":
        form = forms.ProductGroupAddForm(request.POST, request.FILES)
        if form.is_valid():
            new_group: ProductGroup = form.save(commit=False)
            new_group.user = request.user
            if request.ms_store is not None:
                new_group.store = request.ms_store
            new_group.save_with_message(request)
            return redirect(reverse("ms_products:groups"))
    else:
        form = forms.ProductGroupAddForm()

    vue_apps = [
        vue_models.AppDataMIS(
            APP_TAG="#product-vendor",
            misApiEndpoint=reverse("ms_products_api:vendors_modal"),
            misTitle=_("Choose a vendor"),
            misItemName=_("Vendor"),
            misModalId="product-vendor-modal",
            misInputName="vendor",
            misRequired=True,
        )
    ]
    context = {"form": form, "show_edit_warning": False, "vue_apps_json": vue_models.get_json(vue_apps)}
    return render(request, "mobishopper/products/groups_add_edit.html", _("Add product group"), context)


@permissions_required_products
def groups_edit(request, id):
    """Edit a product group."""
    group = get_object_or_404(ProductGroup, id=id)
    if not editable_in_store_context(request, group):
        raise PermissionDenied()
    if request.method == "POST":
        old_group = ProductGroup.objects.get(id=id)
        form = forms.ProductGroupEditForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            new_group: ProductGroup = form.save(commit=False)
            new_group.id = None
            new_group.pk = None
            new_group.user = request.user
            if request.ms_store is not None:
                new_group.store = request.ms_store

            new_group.save_as_replacement(request, old_group)
            return redirect(reverse("ms_products:groups_edit", args=(new_group.id,)))
    else:
        form = forms.ProductGroupEditForm(instance=group)
        now = django.utils.timezone.now()
        if group.date_ended and group.date_ended >= now:
            form.initial["date_started"] = group.date_ended
        else:
            form.initial["date_started"] = now
        form.initial["date_ended"] = None

    vendor_initial = []
    vendor_name = ""
    if group.vendor:
        vendor_initial = [
            vue_models.ModalItem(
                id=group.vendor.id, name=group.vendor.name, details_url=group.vendor.get_absolute_url()
            )
        ]
        vendor_name = group.vendor.name

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
        )
    ]
    context = {
        "form": form,
        "show_edit_warning": True,
        "vue_apps_json": vue_models.get_json(vue_apps),
        "vendor_name": vendor_name,
    }
    return render(
        request, "mobishopper/products/groups_add_edit.html", _("Edit product group {0}").format(group.name), context
    )


@permissions_required_products
def groups_delete(request, id):
    """Delete a product group."""
    group = get_object_or_404(ProductGroup, id=id)
    destination = reverse("ms_products:groups")

    if not editable_in_store_context(request, group):
        raise PermissionDenied()

    if request.method == "POST" and "confirm" in request.POST:
        now = django.utils.timezone.now()
        products = Product.objects.filter(filter_in_effect(now), group=group)
        group.date_ended = now
        success = group.save_with_error_message(request)

        if success:
            for product in products:
                old_id = product.id
                product.pk = None
                product.id = None
                product.group = None
                product.date_started = now
                old_product = Product.objects.get(id=old_id)
                product.save_as_replacement(request, old_product, quiet=True)
            messages.info(request, _("{} has been deleted.").format(group))
        return redirect(destination)

    extra_text = _(
        "Deleting a product group will create new revisions of products in the group, with no group set. Those revisions will be valid immediately."
    )
    return render_delete_get(request, group, destination, extra_text)


@permissions_required_products
def groups_search(request):
    """Show full product group search page."""
    form = forms.ProductGroupFilterForm()
    context = {"form": form, "action_url": reverse("ms_products:groups"), "show_product_only_fields": False}
    return render(request, "mobishopper/products/products_search.html", _("Search groups"), context)


@permissions_required_products_global
def properties_list(request):
    """Show all standard properties."""
    properties = StandardMetaField.objects.order_by("name").annotate(
        required_count=Count("subcategories_required"), recommended_count=Count("subcategories_recommended")
    )

    paginator, page = paginate(properties, request)
    context = {"paginator": paginator, "properties": page, "add_button_dest": reverse("ms_products:properties_add")}
    return render(request, "mobishopper/products/properties_list.html", _("Standard properties"), context)


@permissions_required_products_global
def properties_add(request):
    """Add a standard property."""
    if request.method == "POST":
        form = forms.StandardMetaFieldForm(request.POST)
        if form.is_valid():
            custom_units_text = form.cleaned_data["expected_units_custom_text"]
            property: StandardMetaField = form.save(commit=False)
            property.expected_units_custom_set = [i for i in map(str.strip, custom_units_text.split("\n")) if i]
            property.save_with_message(request)
            form.save_m2m()
            return redirect("ms_products:properties")
    else:
        form = forms.StandardMetaFieldForm()

    return render(request, "mobishopper/products/properties_add_edit.html", _("Add standard property"), {"form": form})


@permissions_required_products_global
def properties_edit(request, id):
    """Edit a standard property."""
    property = get_object_or_404(StandardMetaField, id=id)
    if request.method == "POST":
        form = forms.StandardMetaFieldForm(request.POST, instance=property)
        if form.is_valid():
            custom_units_text = form.cleaned_data["expected_units_custom_text"]
            property: StandardMetaField = form.save(commit=False)
            if property.expected_units == "_custom_set":
                property.expected_units_custom_set = [i for i in map(str.strip, custom_units_text.split("\n")) if i]
            else:
                property.expected_units_custom_set = []
            property.save_with_message(request)
            form.save_m2m()
            return redirect(property.get_absolute_url())
    else:
        form = forms.StandardMetaFieldForm(instance=property)

    form.initial["expected_units_custom_text"] = "\n".join(property.expected_units_custom_set)

    return render(
        request,
        "mobishopper/products/properties_add_edit.html",
        _("Edit standard property {0}").format(property.name),
        {"form": form},
    )


@permissions_required_products_global
def properties_delete(request, id):
    """Delete a standard property."""
    property = get_object_or_404(StandardMetaField, id=id)
    destination = reverse("ms_products:properties")
    return render_delete(request, property, destination, destination)


@permissions_required_products
def vendors_list(request):
    """Show all vendors."""
    form = forms.VendorFilterForm(request.GET)
    order = request.GET.get("order", "name")
    filters = []
    filters_dict = {}
    if form.is_valid():
        if form.cleaned_data["name"]:
            filters_dict["name"] = form.cleaned_data["name"]
        if form.cleaned_data["valid_at"]:
            filters.append(filter_in_effect(form.cleaned_data["valid_at"]))
        else:
            filters.append(filter_in_effect())
        if form.cleaned_data["is_store"]:
            filters_dict["store__isnull"] = False
    else:
        filters.append(filter_in_effect())
        form.initial["valid_at"] = django.utils.timezone.now()

    if request.ms_store is not None and "store__isnull" not in filters_dict:
        filters.append(Q(store=None) | Q(store=request.ms_store))

    vendors = (
        Vendor.objects.filter(*filters, **filters_dict)
        .order_by(order)
        .annotate(size=Count("product", filter=filter_in_effect(prefix="product__")))
    )

    paginator, page = paginate(vendors, request)
    context = {
        "paginator": paginator,
        "vendors": page,
        "add_button_dest": reverse("ms_products:vendors_add"),
        "order": order,
        "show_order": True,
        "search_form": form,
    }
    return render(request, "mobishopper/products/vendors_list.html", _("Vendors"), context)


@permissions_required_products
def vendors_show(request, id):
    """Show a vendor’s products."""
    vendor = get_object_or_404(Vendor, id=id)
    products = Product.objects.filter(vendor=vendor)
    show_all = "all" in request.GET
    if not show_all:
        products = products.filter(filter_in_effect())
    return render(
        request,
        "mobishopper/products/vendors_show.html",
        _("Products of vendor {0}").format(vendor.name),
        {"vendor": vendor, "products": products, "show_all": show_all},
    )


@permissions_required_products
def vendors_add(request):
    """Add a vendor."""
    if request.method == "POST":
        form = forms.VendorAddForm(request.POST, request.FILES)
        if form.is_valid():
            new_vendor: Vendor = form.save(commit=False)
            new_vendor.user = request.user
            if request.ms_store is not None:
                new_vendor.store = request.ms_store

            new_vendor.save_with_message(request)
            return redirect(reverse("ms_products:vendors"))
    else:
        form = forms.VendorAddForm()

    context = {"form": form, "show_edit_warning": False}
    return render(request, "mobishopper/products/vendors_add_edit.html", _("Add vendor"), context)


@permissions_required_products
def vendors_edit(request, id):
    """Edit a vendor."""
    vendor = get_object_or_404(Vendor, id=id)
    if not editable_in_store_context(request, vendor):
        raise PermissionDenied()
    if request.method == "POST":
        old_vendor = Vendor.objects.get(id=id)
        form = forms.VendorEditForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            new_vendor: Vendor = form.save(commit=False)
            new_vendor.id = None
            new_vendor.pk = None
            new_vendor.user = request.user
            if request.ms_store is not None:
                new_vendor.store = request.ms_store

            new_vendor.save_as_replacement(request, old_vendor)
            return redirect(reverse("ms_products:vendors_edit", args=(new_vendor.id,)))
    else:
        form = forms.VendorEditForm(instance=vendor)
        now = django.utils.timezone.now()
        if vendor.date_ended and vendor.date_ended >= now:
            form.initial["date_started"] = vendor.date_ended
        else:
            form.initial["date_started"] = now
        form.initial["date_ended"] = None

    context = {"form": form, "show_edit_warning": True}
    return render(
        request, "mobishopper/products/vendors_add_edit.html", _("Edit vendor {0}").format(vendor.name), context
    )
