"""REST API views for ms_userdata."""

import datetime
from uuid import uuid4

import django.utils.timezone
import rest_framework.exceptions
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _
from rest_framework import generics, mixins
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from ms_baseline import constants
from ms_baseline.models import MsUser
from ms_baseline.serializers import (
    JSONDecimalParser,
    SerializerContextMixin,
    SimpleUserSerializer,
    get_serializer_context,
)
from ms_products.constants import PREFETCH_PRODUCT_BASIC, PREFETCH_SHOPPING_LIST
from ms_products.models import Product
from ms_userdata.models import ShoppingList, ShoppingListEntry, ShoppingListInvite
from ms_userdata.serializers import ShoppingListEntrySerializer, ShoppingListInviteSerializer, ShoppingListSerializer

login_required_drf = permission_classes([IsAuthenticated])


@login_required_drf
@api_view(["POST", "DELETE"])
def shopping_list_share(request: Request, pk: int):
    """Manage shopping list sharing."""
    shopping_list: ShoppingList = get_object_or_404(ShoppingList, id=pk, user=request.user)
    if request.method == "POST":
        shopping_list.sharing_uuid = uuid4()
    else:
        shopping_list.sharing_uuid = None
    shopping_list.save()
    return Response({"sharing_uuid": shopping_list.sharing_uuid, "sharing_url": shopping_list.get_sharing_url(request)})


class ShoppingListsList(SerializerContextMixin, mixins.ListModelMixin, generics.GenericAPIView):
    """List shopping lists, or create a new one."""

    serializer_class = ShoppingListSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONDecimalParser]

    def get_queryset(self):
        """Get the queryset for the shopping lists list."""
        return (
            ShoppingList.objects.prefetch_related(*PREFETCH_SHOPPING_LIST)
            .filter(filter_list_access(self.request.user))
            .distinct()
        )

    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        for sl in self.get_queryset():
            sl.upgrade_products()
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST requests."""
        instance = ShoppingList(name=request.data["name"], store_id=request.data["store"], user=request.user)
        instance.save()
        return Response(ShoppingListSerializer(instance).data, status=201)


class ShoppingListDetail(
    SerializerContextMixin,
    mixins.DestroyModelMixin,
    generics.GenericAPIView,
):
    """Show details of a shopping list, update it, or destroy it."""

    serializer_class = ShoppingListSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONDecimalParser]

    def get_queryset(self):
        """Get the queryset for the shopping lists list."""
        return ShoppingList.objects.prefetch_related(*PREFETCH_SHOPPING_LIST).filter(
            filter_list_access(self.request.user)
        )

    def perform_destroy(self, instance):
        """Perform the destruction of the instance."""
        if self.request.user != instance.user:
            raise rest_framework.exceptions.PermissionDenied("Only the owner can delete lists.")
        return super().perform_destroy(instance)

    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        instance: ShoppingList = self.get_object()
        any_changes = instance.upgrade_products(allow_ignore=False)

        if any_changes:
            instance = self.get_object()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        """Handle PATCH requests."""
        instance: ShoppingList = self.get_object()
        if request.user != instance.user:
            raise rest_framework.exceptions.PermissionDenied("Only the owner can change list properties.")
        instance.name = request.data["name"]
        instance.store_id = request.data["store"]
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        """Handle DELETE requests."""
        return self.destroy(request, *args, **kwargs)


@login_required_drf
@api_view(["GET", "POST", "DELETE"])
@parser_classes([JSONDecimalParser])
def shopping_list_entry(request, pk: int, product_pk: int):
    """Show, add, modify or delete a product on a shopping list. Takes POST data with `amount` and `bought` as keys."""
    shopping_list: ShoppingList = get_object_or_404(
        ShoppingList.objects.prefetch_related("entries"), filter_list_access(request.user), pk=pk
    )
    product: Product = get_object_or_404(Product.objects.prefetch_related(*PREFETCH_PRODUCT_BASIC), pk=product_pk)
    entry: ShoppingListEntry = shopping_list.entries.filter(product=product).first()
    status = 200

    if request.method in ("GET", "DELETE"):
        if not entry:
            raise rest_framework.exceptions.NotFound()

    if request.method == "DELETE":
        entry.delete()
        return Response(None, 204)
    elif request.method == "POST":
        amount = request.data.get("amount", 1)
        bought = request.data.get("bought")

        if not entry:
            status = 201
            entry = ShoppingListEntry(list=shopping_list, product=product, bought=False)
        entry.amount = amount
        if bought is not None:
            entry.bought = bought
        entry.user = request.user
        entry.save()

    return Response(ShoppingListEntrySerializer(entry, context=get_serializer_context(request=request)).data, status)


class ShoppingListInviteList(SerializerContextMixin, mixins.ListModelMixin, generics.GenericAPIView):
    """List or create shopping list invites."""

    serializer_class = ShoppingListInviteSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get the queryset for the shopping list invites list."""
        now_minus_expiry = django.utils.timezone.now() - datetime.timedelta(days=constants.INVITE_EXPIRATION_DAYS)
        return ShoppingListInvite.objects.filter(
            list=self.kwargs["list_pk"], date_added__gte=now_minus_expiry, used=False
        )

    def perform_create(self, serializer):
        """Create an invite and send the invite e-mail."""
        shopping_list = get_object_or_404(ShoppingList, pk=self.kwargs["list_pk"])
        invite: ShoppingListInvite = serializer.save(list=shopping_list)
        invite.send_email(self.request)
        return invite

    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        shopping_list = get_object_or_404(ShoppingList, pk=self.kwargs["list_pk"])
        if shopping_list.can_access(request.user):
            return self.list(request, *args, **kwargs)
        else:
            raise rest_framework.exceptions.PermissionDenied(_("You cannot access this list."))

    def post(self, request, *args, **kwargs):
        """Handle POST requests."""
        shopping_list = get_object_or_404(ShoppingList, pk=self.kwargs["list_pk"])
        if shopping_list.user != request.user:
            raise rest_framework.exceptions.PermissionDenied(_("Cannot create invites for this list."))

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite = self.perform_create(serializer)
        return Response(self.get_serializer(invite).data, status=201)


class ShoppingListInviteDetail(
    SerializerContextMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView
):
    """Show or delete a shopping list invite."""

    serializer_class = ShoppingListInviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get the queryset for the shopping list invites list."""
        return ShoppingListInvite.objects.filter(list=self.kwargs["list_pk"])

    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        shopping_list = get_object_or_404(ShoppingList, pk=self.kwargs["list_pk"])
        if shopping_list.can_access(request.user):
            return self.retrieve(request, *args, **kwargs)
        else:
            raise rest_framework.exceptions.PermissionDenied(_("You cannot access this list."))

    def delete(self, request, *args, **kwargs):
        """Handle DELETE requests."""
        instance = self.get_object()
        if instance.list.user != request.user:
            raise rest_framework.exceptions.PermissionDenied(_("Cannot delete invites for this list."))

        return self.destroy(request, *args, **kwargs)


@login_required_drf
@api_view(["GET", "POST"])
def invite_details_accept(request, uuid: uuid4):
    """Show the details of an invite or accept it."""
    invite: ShoppingListInvite = get_object_or_404(ShoppingListInvite, id=uuid)
    if invite.is_expired():
        raise rest_framework.exceptions.PermissionDenied(_("Invite has expired."))
    if request.method == "GET":
        return Response({"user": invite.list.user.get_full_name(), "name": invite.list.name})
    else:
        with transaction.atomic():
            invite.used = True
            invite.save()
            invite.list.shared_with.add(request.user)
        return Response(ShoppingListSerializer(invite.list, context=get_serializer_context(request=request)).data)


@login_required_drf
@api_view(["DELETE"])
def remove_list_member(request, pk: int, user_pk: int):
    """Remove a list member."""
    shopping_list: ShoppingList = get_object_or_404(ShoppingList, user=request.user, pk=pk)
    user = get_object_or_404(MsUser, pk=user_pk)
    if request.user == user or request.user == shopping_list.user:
        if shopping_list.shared_with.filter(id=user.id):
            shopping_list.shared_with.remove(user)
            return Response(_("Removed successfully."), status=200)
        else:
            raise rest_framework.exceptions.NotFound(_("List member not found."))
    else:
        raise rest_framework.exceptions.PermissionDenied(_("Cannot remove list members."))


@login_required_drf
@api_view(["GET", "DELETE"])
def get_delete_list_members(request, pk: int):
    """Get list members or leave a shopping list owned by a different user."""
    shopping_list: ShoppingList = get_object_or_404(ShoppingList, filter_list_access(request.user), pk=pk)
    if request.method == "DELETE":
        if shopping_list.user == request.user:
            raise rest_framework.exceptions.PermissionDenied()
        shopping_list.shared_with.remove(request.user)

    return Response(
        {
            "shared_with": SimpleUserSerializer(shopping_list.shared_with.all(), many=True).data,
            "owner": SimpleUserSerializer(shopping_list.user).data,
        }
    )


@login_required_drf
@api_view(["POST"])
def shopping_list_clean_done_items(request, pk: int):
    """Remove complete items from a shopping list."""
    shopping_list: ShoppingList = get_object_or_404(ShoppingList, filter_list_access(request.user), pk=pk)
    for e in shopping_list.entries.all():
        if e.bought:
            e.delete()
    shopping_list.save()
    shopping_list: ShoppingList = get_object_or_404(ShoppingList, filter_list_access(request.user), pk=pk)
    return Response(ShoppingListSerializer(shopping_list, context=get_serializer_context(request=request)).data)


def filter_list_access(user):
    """Filter shopping lists that the user can access."""
    return Q(user=user) | Q(shared_with=user)
