"""Utilities for ms_products."""
import decimal

from django.utils.translation import gettext as _

from ms_baseline.utils import format_money


def prepare_per_amount(price: decimal.Decimal, amount: decimal.Decimal, amount_unit: str) -> (str, decimal.Decimal):
    """Convert an price, an amount and a unit to an appropriate generalized price and amount."""
    HALF = decimal.Decimal("0.5")
    TENTH = decimal.Decimal("0.1")

    if amount_unit == "1":
        return "1", price / amount

    if amount_unit == "dag":
        if amount >= 50:
            return "1 kg", price * 100 / amount
        else:
            return "100 g", price * 10 / amount

    if amount_unit == "g":
        if amount >= 500:
            return "1 kg", price * 1000 / amount
        else:
            return "100 g", price * 100 / amount

    if amount_unit == "kg":
        if amount >= HALF:
            return "1 kg", price * 1 / amount
        else:
            return "100 g", price * TENTH / amount

    if amount_unit == "mL":
        if amount >= 500:
            return "1 L", price * 1000 / amount
        else:
            return "100 mL", price * 100 / amount

    if amount_unit == "L":
        if amount >= HALF:
            return "1 L", price * 1 / amount
        else:
            return "100 mL", price * TENTH / amount

    return "1 " + amount_unit, price * 1 / amount


def get_price_per_amount_str(price: decimal.Decimal, amount: decimal.Decimal, amount_unit: str) -> str:
    """Get the price per amount as a string."""
    unit_display, price_divided = prepare_per_amount(price, amount, amount_unit)
    if unit_display == "1":
        return _("{0} / pc").format(format_money(price_divided))

    return "{0} / {1}".format(format_money(price_divided), unit_display)
