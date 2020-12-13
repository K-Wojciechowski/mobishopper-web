"""Tests for ms_userdata."""
from django.test import TestCase

from ms_baseline.models import MsUser
from ms_products.models import Category, Product, Store, Subcategory, Vendor
from ms_userdata.models import ShoppingList, ShoppingListEntry


class TestShoppingListProductUpgrades(TestCase):
    """Test shopping list upgrades."""

    def setUp(self):
        """Create objects used for testing."""
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
        self.user = MsUser(email="example@example.com")
        self.user.save()

        self.list = ShoppingList(user=self.user, store=self.store)
        self.list.save()
        self.entry = ShoppingListEntry(list=self.list, product=self.product, amount=2, user=self.user)
        self.entry.save()

    def test_simple_upgrades(self):
        """Test simple upgrades of shopping list products."""
        old_product_id = self.product.id
        self.product.name = "test product 2"
        self.product.id = None
        self.product.pk = None
        old_product = Product.objects.get(id=old_product_id)
        self.product.save_as_replacement(None, old_product)

        self.assertEqual(self.list.entries.count(), 1)
        self.assertEqual(self.list.entries.all()[0].product.name, "test product")

        self.list.upgrade_products(allow_ignore=False)

        self.assertEqual(self.list.entries.count(), 1)
        self.assertEqual(self.list.entries.all()[0].product.name, "test product 2")

    def test_merge_upgrades(self):
        """Test upgrades of shopping list products, where two revisions of the same product are on the list."""
        old_product_id = self.product.id
        self.product.name = "test product 2"
        self.product.id = None
        self.product.pk = None
        old_product = Product.objects.get(id=old_product_id)
        self.product.save_as_replacement(None, old_product)
        entry = ShoppingListEntry(list=self.list, product=self.product, amount=4, user=self.user)
        entry.save()

        self.assertEqual(self.list.entries.count(), 2)
        self.assertEqual({i.product.name for i in self.list.entries.all()}, {"test product", "test product 2"})

        self.list.upgrade_products(allow_ignore=False)

        self.assertEqual(self.list.entries.count(), 1)
        self.assertEqual(self.list.entries.all()[0].product.name, "test product 2")

    def test_multi_step_upgrades(self):
        """Test upgrades of shopping list products which had multiple upgrades since the insertion."""
        first_product_id = self.product.id
        self.product.name = "test product 2"
        self.product.id = None
        self.product.pk = None
        first_product = Product.objects.get(id=first_product_id)
        self.product.save_as_replacement(None, first_product)

        second_product_id = self.product.id
        self.product.name = "test product 3"
        self.product.id = None
        self.product.pk = None
        second_product = Product.objects.get(id=second_product_id)
        self.product.save_as_replacement(None, second_product)

        self.assertEqual(self.list.entries.count(), 1)
        self.assertEqual(self.list.entries.all()[0].product.name, "test product")

        self.list.upgrade_products(allow_ignore=False)

        self.assertEqual(self.list.entries.count(), 1)
        self.assertEqual(self.list.entries.all()[0].product.name, "test product 3")
