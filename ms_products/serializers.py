"""REST serializers for ms_products."""
from rest_framework import serializers

from ms_baseline.utils import filter_in_effect, filter_in_effect_visited_store
from ms_products import models
from ms_products.utils import get_price_per_amount_str


class CategorySerializer(serializers.ModelSerializer):
    """A serializer for Categories."""

    class Meta:
        model = models.Category
        fields = ["id", "name", "description"]


class SubcategorySerializer(serializers.ModelSerializer):
    """A serializer for Subcategories."""

    parent = CategorySerializer()

    class Meta:
        model = models.Subcategory
        fields = ["id", "name", "description", "parent"]


class VendorSerializer(serializers.ModelSerializer):
    """A serializer for Vendors."""

    class Meta:
        model = models.Vendor
        fields = ["id", "name", "logo", "description", "website"]


class ProductBaseSerializer(serializers.ModelSerializer):
    """The base class for Product serializers."""

    vendor = VendorSerializer()
    subcategory = SubcategorySerializer()
    price = serializers.SerializerMethodField()
    available = serializers.SerializerMethodField()
    price_per_amount = serializers.SerializerMethodField()

    def get_override(self, product):
        """Get the product override in effect."""
        return product.localproductoverride_set.filter(filter_in_effect(), store=self.context["store_id"]).last()

    def get_available(self, product):
        """Get the product availability status."""
        override = self.get_override(product)
        if override:
            return override.available
        return True

    def get_price(self, product):
        """Get the product price."""
        override = self.get_override(product)
        if override:
            return str(override.price)
        return str(product.price)

    def get_price_per_amount(self, product):
        """Get the price-per-amount for the product."""
        override = self.get_override(product)
        if override:
            price = override.price
        else:
            price = product.price
        return get_price_per_amount_str(price, product.amount, product.amount_unit)


class ProductBasicSerializer(ProductBaseSerializer):
    """A basic serializer for Products."""

    class Meta:
        model = models.Product
        fields = [
            "id",
            "name",
            "vendor",
            "subcategory",
            "photo",
            "price",
            "amount",
            "amount_unit",
            "any_amount",
            "price_per_amount",
            "date_started",
            "date_ended",
            "available",
        ]


PRODUCT_SERIALIZER_FIELDS = [
    "id",
    "name",
    "vendor",
    "subcategory",
    "photo",
    "price",
    "amount",
    "amount_unit",
    "any_amount",
    "price_per_amount",
    "date_started",
    "date_ended",
    "available",
    "group",
    "description",
    "extra_metadata_raw",
    "override_note",
]


class ProductSerializer(ProductBaseSerializer):
    """A serializer for Products."""

    group = serializers.PrimaryKeyRelatedField(read_only=True)
    override_note = serializers.SerializerMethodField()

    def get_override_note(self, product):
        """Get the product override note."""
        override = self.get_override(product)
        if override:
            return override.note
        return None

    class Meta:
        model = models.Product
        fields = PRODUCT_SERIALIZER_FIELDS


class CurrentListSerializer(serializers.ListSerializer):
    """Serialize a QuerySet, filtering it to products in effects only."""

    def to_representation(self, data):
        """Convert a QuerySet to its representation."""
        data = data.filter(filter_in_effect_visited_store(self.context["request"]))
        return super().to_representation(data)


class ProductCurrentSerializer(ProductSerializer):
    """A serializer for Products that always filters them to products in effect only."""

    class Meta:
        list_serializer_class = CurrentListSerializer
        model = models.Product
        fields = PRODUCT_SERIALIZER_FIELDS


class ProductGroupSerializer(serializers.ModelSerializer):
    """A serializer for ProductGroups."""

    vendor = VendorSerializer()
    subcategory = SubcategorySerializer()
    products = ProductCurrentSerializer(many=True, read_only=True)

    class Meta:
        model = models.ProductGroup
        fields = ["id", "name", "description", "photo", "vendor", "subcategory", "products"]
