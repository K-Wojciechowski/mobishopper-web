"""Tests for ms_maps."""
from django.test import TestCase

from ms_baseline.models import Store
from ms_maps import auto_assign
from ms_maps.models import Aisle, ProductLocation, Subaisle
from ms_products.models import Category, Product, Subcategory, Vendor


class TestAutoAssign(TestCase):
    """Test automated product location assignment."""

    def setUp(self):
        """Create models."""
        self.category = Category(name="test category")
        self.category.save()
        self.subcategory = Subcategory(name="test subcategory", parent=self.category)
        self.subcategory.save()
        self.vendor = Vendor(name="test vendor")
        self.vendor.save()
        self.product = Product(
            name="test product", price=1, amount=1, amount_unit="pc", subcategory=self.subcategory, vendor=self.vendor
        )
        self.product.save()

        self.store = Store(name="test store")
        self.store.save()
        self.aisle = Aisle(name="test aisle", store=self.store)
        self.aisle.save()
        self.subaisle1 = Subaisle(name="test subaisle 1", parent=self.aisle, store=self.store)
        self.subaisle1.save()
        self.subaisle1.subcategories.set([self.subcategory])
        self.subaisle2 = Subaisle(name="test subaisle 2", parent=self.aisle, store=self.store)
        self.subaisle2.save()

    def tearDown(self):
        """Delete the product."""
        self.product.delete()

    def test_assign_by_method(self):
        """Test a single auto-assignment by method."""
        location = ProductLocation.create_auto_location(self.product, self.store)
        self.assertEqual(location.subaisle.id, self.subaisle1.id)
        location.subaisle = self.subaisle2
        location.save()

        # is_auto will result in an override
        self.assertEqual(location.subaisle.id, self.subaisle2.id)
        location.compute_auto_location()
        self.assertEqual(location.subaisle.id, self.subaisle1.id)

        location.subaisle = self.subaisle2
        location.is_auto = False
        location.save()

        # without is_auto, force is required
        self.assertEqual(location.subaisle.id, self.subaisle2.id)
        location.compute_auto_location()
        self.assertEqual(location.subaisle.id, self.subaisle2.id)
        location.compute_auto_location(force=True)
        self.assertEqual(location.subaisle.id, self.subaisle1.id)

        # if a subcategory appears multiple times, is_auto becomes False
        subaisle3 = Subaisle(name="test subaisle 3", parent=self.aisle, store=self.store)
        subaisle3.save()
        subaisle3.subcategories.set([self.subcategory])
        self.assertFalse(location.compute_auto_location(force=True))
        subaisle3.delete()

    def _test_bulk_assign(self, expected):
        """Test auto-assignment by the bulk asisgnment command."""
        logger = auto_assign.AutoAssignHtmlLogWriter()
        old_level = auto_assign.py_logger.level
        try:
            auto_assign.py_logger.setLevel(99)

            self.assertEqual(auto_assign.auto_assign(logger, [self.store]), expected)
        finally:
            auto_assign.py_logger.setLevel(old_level)

    def test_bulk_assign_success(self):
        """Test successful auto-assignment by the bulk asisgnment command."""
        self._test_bulk_assign(1)
        loc = ProductLocation.objects.get(store=self.store, product=self.product)
        self.assertEqual(loc.subaisle.id, self.subaisle1.id)

        # Repeating assignment should not do anything.
        self._test_bulk_assign(0)

    def test_bulk_assign_failure(self):
        """Test failure of auto-assignment by the bulk asisgnment command due to multiple aisles."""
        subaisle3 = Subaisle(name="test subaisle 3", parent=self.aisle, store=self.store)
        subaisle3.save()
        subaisle3.subcategories.set([self.subcategory])
        self._test_bulk_assign(0)
        with self.assertRaises(ProductLocation.DoesNotExist):
            ProductLocation.objects.get(store=self.store, product=self.product)

        subaisle3.delete()
