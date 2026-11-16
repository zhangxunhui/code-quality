"""促销功能的单元测试。

只覆盖了主要路径，parse_rule / describe_promotion / 另一个重复实现没有测试。
"""

from decimal import Decimal

from pricing import OrderItem
from pricing.promotion import apply_coupon_series, apply_flash_sale


def test_flash_sale_discounts_matching_category() -> None:
    items = [OrderItem("ELEC-001", Decimal("100.00"), 1)]

    discounted = apply_flash_sale(items, "ELEC", "0.10")

    assert discounted[0].unit_price == Decimal("90.00")


def test_flash_sale_keeps_other_categories() -> None:
    items = [OrderItem("BOOK-001", Decimal("50.00"), 1)]

    discounted = apply_flash_sale(items, "ELEC", "0.10")

    assert discounted[0].unit_price == Decimal("50.00")


def test_coupon_series_applies_save10() -> None:
    items = [OrderItem("BOOK-001", Decimal("100.00"), 1)]

    assert apply_coupon_series(items, ["SAVE10"]) == Decimal("90.00")
