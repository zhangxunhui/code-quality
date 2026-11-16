"""数据模型行为的单元测试。"""

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from pricing import OrderItem


def test_default_discount_rate_is_zero() -> None:
    item = OrderItem(sku="SKU-001", unit_price=Decimal("10.00"), quantity=1)
    assert item.discount_rate == Decimal("0")


def test_order_item_is_immutable() -> None:
    item = OrderItem(sku="SKU-001", unit_price=Decimal("10.00"), quantity=1)
    with pytest.raises(FrozenInstanceError):
        item.quantity = 2  # type: ignore[misc]


def test_items_with_same_values_are_equal() -> None:
    left = OrderItem(sku="SKU-001", unit_price=Decimal("10.00"), quantity=2)
    right = OrderItem(sku="SKU-001", unit_price=Decimal("10.00"), quantity=2)
    assert left == right
