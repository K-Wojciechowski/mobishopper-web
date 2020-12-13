"""REST serializers for ms_products."""
from rest_framework import serializers

from ms_maps import models
from ms_products.serializers import ProductBasicSerializer, SubcategorySerializer


class AisleSerializer(serializers.ModelSerializer):
    """A serializer for Aisles."""

    class Meta:
        model = models.Aisle
        fields = ["id", "name", "description", "display_code"]


class SubaisleSerializer(serializers.ModelSerializer):
    """A serializer for Subaisles."""

    parent = AisleSerializer()
    subcategories = SubcategorySerializer(many=True)

    class Meta:
        model = models.Subaisle
        fields = ["id", "name", "description", "display_code", "parent", "subcategories"]


class MapTileSerializer(serializers.ModelSerializer):
    """A serializer for MapTiles."""

    map = serializers.PrimaryKeyRelatedField(read_only=True)
    subaisle = SubaisleSerializer(read_only=True)

    class Meta:
        model = models.MapTile
        fields = ["id", "x", "y", "tile_type", "subaisle", "color", "color_is_light", "map"]


class MapSerializer(serializers.ModelSerializer):
    """A serializer for Maps."""

    store = serializers.PrimaryKeyRelatedField(read_only=True)
    tiles = MapTileSerializer(many=True)

    class Meta:
        model = models.Map
        fields = ["id", "store", "width", "height", "tiles"]


class ProductLocationSerializer(serializers.ModelSerializer):
    """A serializer for ProductLocations."""

    product = ProductBasicSerializer()
    tile = MapTileSerializer()
    subaisle = SubaisleSerializer()

    class Meta:
        model = models.ProductLocation
        fields = ["product", "tile", "subaisle"]
