"""API responses for ms_deals."""

import attr
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.utils.translation import gettext as _

from ms_baseline.permission_helpers import permissions_required_deals
from ms_baseline.utils import filter_in_effect_after, filter_this_store_m2m, format_money
from ms_baseline.vue_models import ModalItem, ModalItemContainer
from ms_deals.models import Coupon


@permissions_required_deals
def list_coupons_modal(request):
    """Return a list of coupons for the modal list."""
    queryset = Coupon.objects.order_by("name").filter(filter_in_effect_after())
    if request.ms_store is not None:
        queryset = queryset.filter(filter_this_store_m2m(request) | Q(is_global=True))
    query = request.GET.get("q", "").strip()
    if query:
        queryset = queryset.filter(**{"name" + "__icontains": query})
    paginator = Paginator(queryset, settings.MOBISHOPPER_MODAL_PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page", 1))
    data = [
        ModalItem(
            id=c.id,
            name=c.name,
            details_url=reverse("ms_deals:coupons_show_edit", args=(c.id,)),
            photo=None,
            extras=[c.product.name, format_money(c.price), _("yes") if c.is_global else _("no")],
        )
        for c in page.object_list
    ]
    return JsonResponse(
        attr.asdict(ModalItemContainer(items=list(data), page=page.number, num_pages=paginator.num_pages))
    )
