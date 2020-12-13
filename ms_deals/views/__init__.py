"""Deal management views."""
import datetime
import typing

import django.utils.timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from ms_baseline import vue_models
from ms_baseline.permission_helpers import PermissionDenied, permissions_required_deals
from ms_baseline.utils import (
    filter_in_effect,
    filter_in_effect_this_store_deals_m2m,
    filter_this_store_deals_m2m,
    paginate,
    render,
)
from ms_deals import forms
from ms_deals.models import Coupon, CouponSet, Deal, DealsModelType
from ms_products.models import Product
from ms_userdata.models import CouponSetUse, CouponUse


@permissions_required_deals
def deals_overview(request):
    """Show an overview of deals."""
    now = django.utils.timezone.now()
    now_24h = now - datetime.timedelta(days=1)
    now_7d = now - datetime.timedelta(days=7)
    context = {
        "deals_in_effect": Deal.objects.filter(filter_in_effect_this_store_deals_m2m(request, now)).count(),
        "coupons_in_effect": Coupon.objects.filter(filter_in_effect_this_store_deals_m2m(request, now)).count(),
        "coupon_sets_in_effect": CouponSet.objects.filter(filter_in_effect_this_store_deals_m2m(request, now)).count(),
        "coupons_last_24h": CouponUse.objects.filter(date_modified__gte=now_24h).count(),
        "coupons_last_7d": CouponUse.objects.filter(date_modified__gte=now_7d).count(),
        "coupon_sets_last_7d": CouponSetUse.objects.filter(date_modified__gte=now_7d).count(),
    }

    if request.ms_store is not None:
        store = request.ms_store
        context.update(
            {
                "coupons_store_last_24h": CouponUse.objects.filter(store=store, date_modified__gte=now_24h).count(),
                "coupons_store_last_7d": CouponUse.objects.filter(store=store, date_modified__gte=now_7d).count(),
                "coupon_sets_store_last_7d": CouponSetUse.objects.filter(
                    store=store, date_modified__gte=now_7d
                ).count(),
            }
        )

    return render(request, "mobishopper/deals/deals_overview.html", _("Deals overview"), context)


def _render_list(request, cls, title, add_button_dest, is_coupon_set):
    form = forms.DealCouponSearchForm(request.GET)
    if form.is_valid():
        filters, filters_list = {}, []
        if form.cleaned_data["name"]:
            filters["name__icontains"] = form.cleaned_data["name"]
        if form.cleaned_data["product"] and not is_coupon_set:
            filters["product__name__icontains"] = form.cleaned_data["product"]
        if form.cleaned_data["valid_at"]:
            filters_list.append(filter_in_effect(form.cleaned_data["valid_at"]))
        if form.cleaned_data["is_store"] and request.ms_store is not None:
            filters["stores"] = request.ms_store
        elif request.ms_store is None:
            filters["is_global"] = not form.cleaned_data["is_store"]
        elif request.ms_store is not None:
            filters_list.append(filter_this_store_deals_m2m(request))
    else:
        if request.ms_store is None:
            filters, filters_list = {"is_global": True}, [filter_in_effect()]
        else:
            filters, filters_list = {}, [filter_in_effect(), filter_this_store_deals_m2m(request)]
        form.initial["valid_at"] = django.utils.timezone.now()

    if "valid_at" not in request.GET:
        filters_list.append(filter_in_effect())

    order = request.GET.get("order", "name")
    objects = cls.objects.filter(*filters_list, **filters).order_by(order)

    if is_coupon_set:
        objects = objects.annotate(size=Count("coupons"))

    paginator, page = paginate(objects, request)
    context = {
        "search_form": form,
        "paginator": paginator,
        "page": page,
        "order": order,
        "show_order": True,
        "add_button_dest": add_button_dest,
        "is_coupon_set": is_coupon_set,
    }
    return render(request, "mobishopper/deals/deals_list.html", title, context)


def _product_to_modalitem(id: typing.Optional[int]) -> typing.Optional[vue_models.ModalItem]:
    """Convert a product to a ModalItem (or None if the product does not exist)."""
    if id is None:
        return
    try:
        product: Product = Product.objects.get(id=id)
        return vue_models.ModalItem(id=product.id, name=product.name, details_url=product.get_absolute_url())
    except Product.DoesNotExist:
        return None


def _render_add_form(request, form_cls: typing.Type[forms.AddFormType], title: str, next_url: str):
    """Render the addition form."""
    is_coupon = form_cls == forms.CouponAddForm
    is_coupon_set = form_cls == forms.CouponSetAddForm
    show_product_picker = not is_coupon_set
    show_coupon_picker = is_coupon_set
    initial_product_id = None
    if request.method == "POST":
        form: forms.AddFormType = form_cls(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            if request.ms_store is not None:
                success = instance.save_with_error_message(request)
                form.save_m2m()
                if success:
                    instance.stores.set([request.ms_store])
                    instance.is_global = False
                    instance.save_with_message(request)
            else:
                instance.save_with_message(request)
                form.save_m2m()
            return redirect(next_url)
        elif not is_coupon_set:
            try:
                initial_product_id = int(form.data["product"])
            except ValueError:
                pass
    else:
        form: forms.AddFormType = form_cls()
        if "product" in request.GET and not isinstance(form, forms.CouponSetAddForm):
            try:
                initial_product_id = int(request.GET["product"])
            except ValueError:
                pass

    initial_product_modalitem: typing.Optional[vue_models.ModalItem] = _product_to_modalitem(initial_product_id)
    initial_product_modalitem_list: typing.List[vue_models.ModalItem] = []
    if initial_product_modalitem:
        initial_product_modalitem_list.append(initial_product_modalitem)

    vue_apps = []
    if show_product_picker:
        vue_apps.append(
            vue_models.AppDataMIS(
                APP_TAG="#form-product",
                misApiEndpoint=reverse("ms_products_api:products_modal"),
                misTitle=_("Choose a product"),
                misItemName=_("Product"),
                misModalId="form-product-modal",
                misInputName="product",
                misRequired=True,
                misExtraFieldNames=[_("Vendor"), _("Price")],
                misMultipleSelection=False,
                misInitialSelection=initial_product_modalitem_list,
            )
        )

    if show_coupon_picker:
        vue_apps.append(
            vue_models.AppDataMIS(
                APP_TAG="#form-coupons",
                misApiEndpoint=reverse("ms_deals_api:coupons_modal"),
                misTitle=_("Choose coupons"),
                misItemName=_("Coupon"),
                misModalId="form-coupons-modal",
                misInputName="coupons",
                misRequired=True,
                misExtraFieldNames=[_("Product"), _("Price"), _("Is global")],
                misMultipleSelection=True,
            )
        )

    context = {
        "form": form,
        "vue_apps_json": vue_models.get_json(vue_apps),
        "is_coupon": is_coupon,
        "is_coupon_set": is_coupon_set,
    }
    return render(request, "mobishopper/deals/deals_add.html", title, context)


def _render_show_edit(request, instance: DealsModelType, title: str):
    """Render details/editing form for a deals object."""
    if instance.applies_in(request.ms_store) is False:  # None means store is None
        raise PermissionDenied()
    is_coupon = isinstance(instance, Coupon)
    is_coupon_set = isinstance(instance, CouponSet)
    can_edit = request.ms_store is None or (instance.stores.count() == 1 and instance.stores.filter(id=1))
    form = None
    if can_edit and request.method == "POST":
        form = forms.ValidDateNameChangeForm(request.POST)
        if form.is_valid():
            instance.name = form.cleaned_data["name"]
            instance.date_started = form.cleaned_data["date_started"]
            instance.date_ended = form.cleaned_data["date_ended"]
            instance.user = request.user
            instance.save_with_message(request)
    elif can_edit:
        form = forms.ValidDateNameChangeForm(
            initial={"name": instance.name, "date_started": instance.date_started, "date_ended": instance.date_ended}
        )

    part_of_coupon_sets = []
    if is_coupon:
        part_of_coupon_sets = CouponSet.objects.filter(filter_in_effect(), coupons=instance)

    context = {
        "object": instance,
        "form": form,
        "is_coupon": is_coupon,
        "is_coupon_set": is_coupon_set,
        "part_of_coupon_sets": part_of_coupon_sets,
        "show_editing": can_edit,
    }
    return render(request, "mobishopper/deals/deals_show_edit.html", title, context)


@permissions_required_deals
def deals_list(request):
    """Get a list of deals."""
    return _render_list(request, Deal, _("Deals"), reverse("ms_deals:deals_add"), False)


@permissions_required_deals
def deals_list_store(request):
    """Redirect to a list of deals in store."""
    return redirect(reverse("ms_deals:deals_list") + "?is_store=on")


@permissions_required_deals
def coupons_list(request):
    """Get a list of coupons."""
    return _render_list(request, Coupon, _("Coupons"), reverse("ms_deals:coupons_add"), False)


@permissions_required_deals
def coupon_sets_list(request):
    """Get a list of coupon sets."""
    return _render_list(request, CouponSet, _("Coupon sets"), reverse("ms_deals:coupon_sets_add"), True)


@permissions_required_deals
def deals_add(request):
    """Add a new deal."""
    return _render_add_form(request, forms.DealAddForm, _("Add deal"), reverse("ms_deals:deals_list"))


@permissions_required_deals
def coupons_add(request):
    """Add a new coupon."""
    return _render_add_form(request, forms.CouponAddForm, _("Add coupon"), reverse("ms_deals:coupons_list"))


@permissions_required_deals
def coupon_sets_add(request):
    """Add a new coupon set."""
    return _render_add_form(request, forms.CouponSetAddForm, _("Add coupon set"), reverse("ms_deals:coupon_sets_list"))


@permissions_required_deals
def deals_show_edit(request, id):
    """Show or edit a deal."""
    instance: Deal = get_object_or_404(Deal, id=id)
    return _render_show_edit(request, instance, _("Deal {0}").format(instance.name))


@permissions_required_deals
def coupon_show_edit(request, id):
    """Show or edit a coupon."""
    instance: Coupon = get_object_or_404(Coupon, id=id)
    return _render_show_edit(request, instance, _("Coupon {0}").format(instance.name))


@permissions_required_deals
def coupon_sets_show_edit(request, id):
    """Show or edit a coupon set."""
    instance: CouponSet = get_object_or_404(CouponSet, id=id)
    return _render_show_edit(request, instance, _("Coupon set {0}").format(instance.name))
