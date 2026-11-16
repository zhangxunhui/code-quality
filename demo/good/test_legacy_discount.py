"""适配层的单元测试：新增代码必须自带测试，否则覆盖率门禁会拦住 PR。"""

from decimal import Decimal

import pytest

from pricing import InvalidQuantityError
from pricing.legacy_discount import apply_coupon, calculate


def test_calculate_reuses_core_pricing_rules() -> None:
    items = [
        {"sku": "BOOK-001", "price": "59.90", "qty": 2},
        {"sku": "PEN-010", "price": "3.50", "qty": 12},
    ]

    # 119.80 + 39.90（满 10 件 95 折）
    assert calculate(items) == Decimal("159.70")


def test_calculate_rejects_bad_price() -> None:
    items = [{"sku": "BAD-001", "price": "abc", "qty": 1}]

    with pytest.raises(ValueError, match="不是合法数字"):
        calculate(items)


def test_calculate_rejects_non_positive_quantity() -> None:
    items = [{"sku": "BAD-002", "price": "10.00", "qty": 0}]

    with pytest.raises(InvalidQuantityError):
        calculate(items)


def test_known_coupon_is_applied() -> None:
    assert apply_coupon(Decimal("100.00"), "SAVE10") == Decimal("90.00")


def test_unknown_coupon_is_ignored() -> None:
    assert apply_coupon(Decimal("100.00"), "NOT-EXIST") == Decimal("100.00")


def test_missing_coupon_is_ignored() -> None:
    assert apply_coupon(Decimal("100.00"), None) == Decimal("100.00")
