"""价格计算核心逻辑的单元测试。"""

from decimal import Decimal

import pytest

from pricing import (
    DiscountTooLargeError,
    EmptyOrderError,
    InvalidDiscountRateError,
    InvalidPriceError,
    InvalidQuantityError,
    InvalidTaxRateError,
    OrderItem,
    bulk_discount_rate,
    line_total,
    money,
    order_subtotal,
    order_total,
)


def make_item(
    unit_price: str = "10.00",
    quantity: int = 1,
    discount_rate: str = "0",
) -> OrderItem:
    """构造测试用订单行。"""
    return OrderItem(
        sku="SKU-001",
        unit_price=Decimal(unit_price),
        quantity=quantity,
        discount_rate=Decimal(discount_rate),
    )


class TestMoney:
    def test_rounds_half_up(self) -> None:
        assert money(Decimal("2.345")) == Decimal("2.35")
        assert money(Decimal("2.344")) == Decimal("2.34")

    def test_keeps_two_decimals(self) -> None:
        assert money(Decimal("7")) == Decimal("7.00")


class TestBulkDiscountRate:
    @pytest.mark.parametrize(
        ("quantity", "expected"),
        [
            (1, "0"),
            (9, "0"),
            (10, "0.05"),
            (49, "0.05"),
            (50, "0.10"),
            (99, "0.10"),
            (100, "0.15"),
            (1000, "0.15"),
        ],
    )
    def test_tiers(self, quantity: int, expected: str) -> None:
        assert bulk_discount_rate(quantity) == Decimal(expected)


class TestLineTotal:
    def test_no_discount(self) -> None:
        assert line_total(make_item(quantity=2)) == Decimal("20.00")

    def test_bulk_discount_applies(self) -> None:
        assert line_total(make_item(quantity=10)) == Decimal("95.00")

    def test_bulk_discount_boundary(self) -> None:
        assert line_total(make_item(quantity=50)) == Decimal("450.00")
        assert line_total(make_item(quantity=100)) == Decimal("850.00")

    def test_item_discount_stacks_with_bulk(self) -> None:
        item = make_item(quantity=10, discount_rate="0.02")
        assert line_total(item) == Decimal("93.00")

    def test_discount_sum_may_equal_the_cap(self) -> None:
        item = make_item(quantity=100, discount_rate="0.35")
        assert line_total(item) == Decimal("500.00")

    def test_rejects_discount_above_cap(self) -> None:
        item = make_item(quantity=100, discount_rate="0.40")
        with pytest.raises(DiscountTooLargeError, match="超过上限"):
            line_total(item)

    @pytest.mark.parametrize("quantity", [0, -1])
    def test_rejects_non_positive_quantity(self, quantity: int) -> None:
        with pytest.raises(InvalidQuantityError, match="必须大于 0"):
            line_total(make_item(quantity=quantity))

    def test_rejects_bool_quantity(self) -> None:
        with pytest.raises(InvalidQuantityError, match="必须是整数"):
            line_total(make_item(quantity=True))

    @pytest.mark.parametrize("unit_price", ["0", "-1.00"])
    def test_rejects_non_positive_price(self, unit_price: str) -> None:
        with pytest.raises(InvalidPriceError, match="必须大于 0"):
            line_total(make_item(unit_price=unit_price))

    def test_rejects_float_price(self) -> None:
        item = OrderItem(sku="SKU-001", unit_price=10.5, quantity=1)  # type: ignore[arg-type]
        with pytest.raises(InvalidPriceError, match="Decimal"):
            line_total(item)

    def test_rejects_infinite_price(self) -> None:
        with pytest.raises(InvalidPriceError, match="有限数值"):
            line_total(make_item(unit_price="Infinity"))

    @pytest.mark.parametrize("rate", ["-0.01", "0.51"])
    def test_rejects_discount_out_of_range(self, rate: str) -> None:
        with pytest.raises(InvalidDiscountRateError, match="0 ~ 0.50"):
            line_total(make_item(discount_rate=rate))


class TestOrderSubtotal:
    def test_sums_lines(self) -> None:
        items = [make_item("100.00", 2), make_item("10.00", 10)]
        assert order_subtotal(items) == Decimal("295.00")

    def test_empty_order_is_rejected(self) -> None:
        with pytest.raises(EmptyOrderError):
            order_subtotal([])


class TestOrderTotal:
    def test_applies_tax(self) -> None:
        items = [make_item("100.00", 2)]
        assert order_total(items, Decimal("0.13")) == Decimal("226.00")

    def test_default_tax_is_zero(self) -> None:
        assert order_total([make_item("100.00", 2)]) == Decimal("200.00")

    def test_rejects_tax_out_of_range(self) -> None:
        with pytest.raises(InvalidTaxRateError, match="0 ~ 0.30"):
            order_total([make_item()], Decimal("0.31"))

    def test_rejects_float_tax(self) -> None:
        with pytest.raises(InvalidTaxRateError, match="Decimal"):
            order_total([make_item()], 0.13)  # type: ignore[arg-type]
