"""REST serializers for ms_userdata."""
from rest_framework import serializers

import ms_products.serializers
from ms_baseline.serializers import SimpleUserSerializer
from ms_userdata import models


class ShoppingListEntrySerializer(serializers.ModelSerializer):
    """A serializer for ShoppingListEntries."""

    list = serializers.PrimaryKeyRelatedField(read_only=True)
    product = ms_products.serializers.ProductBasicSerializer(read_only=True)

    class Meta:
        model = models.ShoppingListEntry
        fields = ["id", "list", "product", "amount", "price", "bought"]


class ShoppingListSerializer(serializers.ModelSerializer):
    """A serializer for ShoppingLists."""

    user = SimpleUserSerializer(read_only=True)
    store = serializers.PrimaryKeyRelatedField(read_only=True)
    shared_with = SimpleUserSerializer(many=True, read_only=True)
    sharing_url = serializers.SerializerMethodField()
    entries = ShoppingListEntrySerializer(many=True, read_only=True)
    completion = serializers.IntegerField(read_only=True)

    def get_sharing_url(self, obj: models.ShoppingList):
        """Get the sharing URL of a shopping list."""
        return obj.get_sharing_url(self.context.get("request"))

    class Meta:
        model = models.ShoppingList
        fields = [
            "id",
            "name",
            "user",
            "store",
            "entries",
            "completion",
            "price_cached",
            "sharing_uuid",
            "sharing_url",
            "shared_with",
        ]


class ShoppingListInviteSerializer(serializers.ModelSerializer):
    """A serializer for ShoppingListInvites."""

    id = serializers.UUIDField(read_only=True)
    used = serializers.BooleanField(read_only=True)
    is_expired = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    list = serializers.PrimaryKeyRelatedField(queryset=models.ShoppingList.objects.all())

    def get_is_expired(self, obj: models.ShoppingListInvite):
        """Get list expiration status."""
        return obj.is_expired()

    def get_url(self, obj: models.ShoppingListInvite):
        """Get invite URL."""
        return obj.get_invite_url(self.context["request"])

    class Meta:
        model = models.ShoppingListInvite
        fields = ["id", "email", "used", "is_expired", "list", "url"]
