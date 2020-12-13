"""REST serializers for ms_deals."""
from rest_framework import serializers

import ms_products.serializers
from ms_deals import models


class DealSerializer(serializers.ModelSerializer):
    """A serializer for Deals."""

    type = serializers.SerializerMethodField(source="get_type")
    product = ms_products.serializers.ProductBasicSerializer()
    price_per_amount = serializers.SerializerMethodField(source="get_price_per_amount")

    def get_type(self, value):
        """Get type of the deal."""
        return "DEAL"

    def get_price_per_amount(self, deal: models.Deal):
        """Get price per amount for the deal."""
        return deal.price_per_amount_str

    class Meta:
        model = models.Deal
        fields = ["id", "name", "product", "price", "price_per_amount", "type", "date_started", "date_ended"]


class CouponSerializer(serializers.ModelSerializer):
    """A serializer for Coupons."""

    type = serializers.SerializerMethodField(source="get_type")
    product = ms_products.serializers.ProductBasicSerializer()
    price_per_amount = serializers.SerializerMethodField(source="get_price_per_amount")

    def get_type(self, value):
        """Get type of the deal."""
        return "COUPON"

    def get_price_per_amount(self, coupon: models.Coupon):
        """Get price per amount for the coupon."""
        return coupon.price_per_amount_str

    class Meta:
        model = models.Coupon
        fields = [
            "id",
            "uuid",
            "name",
            "product",
            "price",
            "price_per_amount",
            "one_use",
            "require_account",
            "type",
            "date_started",
            "date_ended",
        ]


class CouponSetSerializer(serializers.ModelSerializer):
    """A serializer for Coupon Sets."""

    type = serializers.SerializerMethodField(source="get_type")
    coupons = CouponSerializer(many=True, read_only=True)

    def get_type(self, value):
        """Get type of the deal."""
        return "COUPON_SET"

    class Meta:
        model = models.CouponSet
        fields = ["id", "uuid", "name", "coupons", "one_use", "require_account", "type", "date_started", "date_ended"]
