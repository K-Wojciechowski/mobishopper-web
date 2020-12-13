"""Tests for ms_products."""
from decimal import Decimal

from django.test import TestCase
from django.utils.translation import gettext as _

from ms_baseline.utils import format_money
from ms_products.utils import get_price_per_amount_str, prepare_per_amount


class TestPricePerAmount(TestCase):
    """Test computing price per amount."""

    def _run_test(self, price, amount, amount_unit, amount_and_unit_str, new_price):
        """Test the unit conversion."""
        self.assertEqual(
            prepare_per_amount(Decimal(price), Decimal(amount), amount_unit), (amount_and_unit_str, Decimal(new_price))
        )

    def test_pieces(self):
        """Test the '1'/pieces unit behaves correctly."""
        self._run_test("1.2", "2", "1", "1", "0.6")
        self._run_test("1.2", "1", "1", "1", "1.2")
        self._run_test("1.2", "0.8", "1", "1", "1.5")

    def test_unknown(self):
        """Test an unknown unit is always switched to 1."""
        self._run_test("1.2", "2", "qwerty", "1 qwerty", "0.6")
        self._run_test("1.2", "1", "qwerty", "1 qwerty", "1.2")
        self._run_test("1.2", "0.8", "qwerty", "1 qwerty", "1.5")
        self._run_test("15", "1200", "qwerty", "1 qwerty", "0.0125")

    def test_dag(self):
        """Test converting dag."""
        self._run_test("1.2", "40", "dag", "100 g", "0.3")
        self._run_test("1.2", "80", "dag", "1 kg", "1.5")
        self._run_test("1.2", "160", "dag", "1 kg", "0.75")

    def test_g(self):
        """Test converting g."""
        self._run_test("1.2", "40", "g", "100 g", "3")
        self._run_test("1.2", "400", "g", "100 g", "0.3")
        self._run_test("1.2", "800", "g", "1 kg", "1.5")
        self._run_test("1.2", "1600", "g", "1 kg", "0.75")

    def test_kg(self):
        """Test converting kg."""
        self._run_test("1.2", "40", "kg", "1 kg", "0.03")
        self._run_test("1.2", "0.4", "kg", "100 g", "0.3")
        self._run_test("1.2", "0.8", "kg", "1 kg", "1.5")
        self._run_test("1.2", "1.6", "kg", "1 kg", "0.75")

    def test_ml(self):
        """Test converting mL."""
        self._run_test("1.2", "40", "mL", "100 mL", "3")
        self._run_test("1.2", "400", "mL", "100 mL", "0.3")
        self._run_test("1.2", "800", "mL", "1 L", "1.5")
        self._run_test("1.2", "1600", "mL", "1 L", "0.75")

    def test_l(self):
        """Test converting L."""
        self._run_test("1.2", "40", "L", "1 L", "0.03")
        self._run_test("1.2", "0.4", "L", "100 mL", "0.3")
        self._run_test("1.2", "0.8", "L", "1 L", "1.5")
        self._run_test("1.2", "1.6", "L", "1 L", "0.75")

    def test_stringify(self):
        """Test stringifying (with decimal formatting and special cases)."""
        self.assertEqual(
            get_price_per_amount_str(Decimal("1.2"), Decimal("2.5"), "1"),
            _("{0} / pc").format(format_money(Decimal("0.48"))),
        )

        self.assertEqual(
            get_price_per_amount_str(Decimal("1.2"), Decimal("40"), "dag"),
            ("{0} / 100 g").format(format_money(Decimal("0.3"))),
        )
