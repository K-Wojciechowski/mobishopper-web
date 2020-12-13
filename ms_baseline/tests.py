"""Tests for ms_baseline."""
import datetime
import types
from decimal import Decimal

import django.utils.timezone
from django.test import TestCase

from ms_baseline.models import Store
from ms_baseline.permission_helpers import editable_in_store_context
from ms_baseline.utils import format_decimal, format_money
from ms_products.models import Category, Product, Subcategory, Vendor


class TestFormatters(TestCase):
    """Test number formatters."""

    def test_format_money(self):
        """Test format_money."""
        nbspzl = "\xa0zł"
        self.assertEqual(format_money(Decimal("0")), "0,00" + nbspzl)
        self.assertEqual(format_money(Decimal("0.01")), "0,01" + nbspzl)
        self.assertEqual(format_money(Decimal("2")), "2,00" + nbspzl)
        self.assertEqual(format_money(Decimal("10")), "10,00" + nbspzl)
        self.assertEqual(format_money(Decimal("12.000")), "12,00" + nbspzl)
        self.assertEqual(format_money(Decimal("42.009")), "42,01" + nbspzl)
        self.assertEqual(format_money(Decimal("1234")), "1234,00" + nbspzl)
        self.assertEqual(format_money(Decimal("12.34")), "12,34" + nbspzl)
        self.assertEqual(format_money(Decimal("0.0000001")), "0,00" + nbspzl)

    def test_format_decimal(self):
        """Test format_decimal."""
        self.assertEqual(format_decimal(Decimal("0")), "0")
        self.assertEqual(format_decimal(Decimal("7")), "7")
        self.assertEqual(format_decimal(Decimal("10")), "10")
        self.assertEqual(format_decimal(Decimal("12345")), "12345")
        self.assertEqual(format_decimal(Decimal("123.045")), "123,045")
        self.assertEqual(format_decimal(Decimal("0.01")), "0,01")
        self.assertEqual(format_decimal(Decimal("0.0001")), "0,0001")
        self.assertEqual(format_decimal(Decimal("1.0123")), "1,0123")


class TestMigrations(TestCase):
    """Test automated migrations for DateRangedTrackedModels."""

    def test_migration_replaced_by(self):
        """Test a migration with a replaced_by field."""
        # Set up vendor and product
        END_DATE = django.utils.timezone.now() + datetime.timedelta(days=5)
        EPSILON = datetime.timedelta(seconds=2)

        category = Category(name="test category")
        category.save()
        subcategory = Subcategory(name="test subcategory", parent=category)
        subcategory.save()
        vendor = Vendor(name="test vendor")
        vendor.save()
        product = Product(
            name="test product",
            price=1,
            amount=1,
            amount_unit="pc",
            date_ended=END_DATE,
            subcategory=subcategory,
            vendor=vendor,
        )
        product.save()

        # Migrate vendor
        start_time = django.utils.timezone.now() - datetime.timedelta(minutes=1)
        vendor2 = Vendor(name="test vendor 2", date_started=start_time)
        vendor2.save_as_replacement(None, vendor)

        # Migrate again, but without date_started
        mid_time = django.utils.timezone.now()
        vendor3 = Vendor(name="test vendor 3")
        vendor3.save_as_replacement(None, vendor2)
        end_time = django.utils.timezone.now()

        # Reload and check product
        product = Product.objects.get(id=product.id)
        self.assertEqual(product.vendor.name, "test vendor")
        self.assertFalse(product.in_effect())
        self.assertIsNone(product.date_started)
        self.assertGreaterEqual(product.date_ended, start_time - EPSILON)
        self.assertLessEqual(product.date_ended, end_time + EPSILON)

        # Check vendors
        self.assertGreaterEqual(vendor.date_ended, start_time - EPSILON)
        self.assertLessEqual(vendor.date_ended, mid_time + EPSILON)

        self.assertGreaterEqual(vendor2.date_started, start_time - EPSILON)
        self.assertLessEqual(vendor2.date_started, mid_time + EPSILON)
        self.assertGreaterEqual(vendor2.date_ended, mid_time - EPSILON)
        self.assertLessEqual(vendor2.date_ended, end_time + EPSILON)

        self.assertGreaterEqual(vendor3.date_started, mid_time - EPSILON)
        self.assertLessEqual(vendor3.date_started, end_time + EPSILON)
        self.assertIsNone(vendor3.date_ended)

        # Check first replacement
        product2 = product.replaced_by
        self.assertEqual(product2.name, product.name)
        self.assertEqual(product2.vendor.name, "test vendor 2")
        self.assertFalse(product2.in_effect())
        self.assertGreaterEqual(product2.date_started, start_time - EPSILON)
        self.assertLessEqual(product2.date_started, mid_time + EPSILON)
        self.assertGreaterEqual(product2.date_ended, mid_time - EPSILON)
        self.assertLessEqual(product2.date_ended, end_time + EPSILON)

        # Check second replacement
        product3 = product2.replaced_by
        self.assertEqual(product3.name, product.name)
        self.assertEqual(product3.vendor.name, "test vendor 3")
        self.assertTrue(product3.in_effect())
        self.assertGreaterEqual(product3.date_started, mid_time - EPSILON)
        self.assertLessEqual(product3.date_started, end_time + EPSILON)
        self.assertEqual(product3.date_ended, END_DATE)


class TestPermissions(TestCase):
    """Test permission-related functions."""

    def test_editable_in_store_context(self):
        """Test editable_in_store_context."""
        store1 = Store(name="S1")
        store2 = Store(name="S2")
        store1.save()
        store2.save()

        vendor0 = Vendor(name="V0")
        vendor1 = Vendor(name="V1", store=store1)
        vendor2 = Vendor(name="V2", store=store2)
        vendor0.save()
        vendor1.save()
        vendor2.save()

        self.assertTrue(editable_in_store_context(types.SimpleNamespace(ms_store=None), vendor0))
        self.assertTrue(editable_in_store_context(types.SimpleNamespace(ms_store=None), vendor1))
        self.assertTrue(editable_in_store_context(types.SimpleNamespace(ms_store=None), vendor2))

        self.assertFalse(editable_in_store_context(types.SimpleNamespace(ms_store=store1), vendor0))
        self.assertTrue(editable_in_store_context(types.SimpleNamespace(ms_store=store1), vendor1))
        self.assertFalse(editable_in_store_context(types.SimpleNamespace(ms_store=store1), vendor2))

        self.assertFalse(editable_in_store_context(types.SimpleNamespace(ms_store=store2), vendor0))
        self.assertFalse(editable_in_store_context(types.SimpleNamespace(ms_store=store2), vendor1))
        self.assertTrue(editable_in_store_context(types.SimpleNamespace(ms_store=store2), vendor2))
