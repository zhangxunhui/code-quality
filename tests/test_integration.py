"""端到端场景：从用户输入一路算到订单总价。"""

from decimal import Decimal

import pytest

from pricing import (
    DiscountTooLargeError,
    EmptyOrderError,
    InvalidQuantityError,
    OrderItem,
    line_total,
    order_subtotal,
    order_total,
    parse_price,
    parse_quantity,
)


def build_cart() -> list[OrderItem]:
    """构造一个包含批量折扣与单品促销的购物车。"""
    return [
        OrderItem("BOOK-001", parse_price("59.90"), parse_quantity("2")),
        OrderItem("PEN-010", parse_price("3.50"), parse_quantity("12")),
        OrderItem(
            "DESK-100",
            parse_price("899.00"),
            parse_quantity("1"),
            Decimal("0.10"),
        ),
    ]


def test_checkout_receipt_matches_expected_amounts() -> None:
    cart = build_cart()

    # 119.80 + 39.90（满 10 件 95 折）+ 809.10（单品 9 折）
    assert order_subtotal(cart) == Decimal("968.80")
    # 968.80 × 1.06 = 1026.928，四舍五入到分
    assert order_total(cart, Decimal("0.06")) == Decimal("1026.93")


def test_quantity_from_user_input_drives_bulk_discount() -> None:
    item = OrderItem("NOTE-001", parse_price("9.99"), parse_quantity(" 10 "))
    assert line_total(item) == Decimal("94.91")


def test_one_invalid_line_aborts_the_whole_order() -> None:
    cart = build_cart()
    cart.append(OrderItem("FREE-001", Decimal("1.00"), 0))

    with pytest.raises(InvalidQuantityError, match="必须大于 0"):
        order_total(cart)


def test_promotion_plus_bulk_discount_cannot_exceed_cap() -> None:
    cart = [OrderItem("BULK-001", Decimal("1.00"), 100, Decimal("0.40"))]

    with pytest.raises(DiscountTooLargeError, match="超过上限"):
        order_total(cart)


def test_empty_cart_is_rejected() -> None:
    with pytest.raises(EmptyOrderError):
        order_total([])
