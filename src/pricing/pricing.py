"""订单金额计算。

金额一律使用 Decimal，避免二进制浮点误差；对外返回的金额统一保留两位小数。
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import ROUND_HALF_UP, Decimal

from .errors import (
    DiscountTooLargeError,
    EmptyOrderError,
    InvalidDiscountRateError,
    InvalidPriceError,
    InvalidQuantityError,
    InvalidTaxRateError,
)
from .models import OrderItem

CENT = Decimal("0.01")
ZERO = Decimal("0")
ONE = Decimal("1")

MAX_DISCOUNT_RATE = Decimal("0.50")
MAX_TAX_RATE = Decimal("0.30")

# (数量门槛, 折扣率)，按门槛从高到低排列。
BULK_TIERS: tuple[tuple[int, Decimal], ...] = (
    (100, Decimal("0.15")),
    (50, Decimal("0.10")),
    (10, Decimal("0.05")),
)


def money(value: Decimal) -> Decimal:
    """把金额四舍五入到分。"""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def bulk_discount_rate(quantity: int) -> Decimal:
    """根据购买数量返回对应的批量折扣率。"""
    for threshold, rate in BULK_TIERS:
        if quantity >= threshold:
            return rate
    return ZERO


def validate_quantity(quantity: int) -> None:
    """校验购买数量为正整数。"""
    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise InvalidQuantityError(f"数量必须是整数，实际为 {quantity!r}")
    if quantity <= 0:
        raise InvalidQuantityError(f"数量必须大于 0，实际为 {quantity}")


def validate_unit_price(unit_price: Decimal) -> None:
    """校验单价为大于 0 的有限数值。"""
    if not isinstance(unit_price, Decimal):
        raise InvalidPriceError(f"单价必须使用 Decimal，实际为 {type(unit_price).__name__}")
    if not unit_price.is_finite():
        raise InvalidPriceError(f"单价必须是有限数值，实际为 {unit_price}")
    if unit_price <= 0:
        raise InvalidPriceError(f"单价必须大于 0，实际为 {unit_price}")


def validate_discount_rate(discount_rate: Decimal) -> None:
    """校验折扣率落在 [0, MAX_DISCOUNT_RATE] 区间内。"""
    if not isinstance(discount_rate, Decimal):
        raise InvalidDiscountRateError("折扣率必须使用 Decimal")
    if not ZERO <= discount_rate <= MAX_DISCOUNT_RATE:
        raise InvalidDiscountRateError(
            f"折扣率必须在 0 ~ {MAX_DISCOUNT_RATE} 之间，实际为 {discount_rate}"
        )


def line_total(item: OrderItem) -> Decimal:
    """计算单行商品在叠加批量折扣后的金额。"""
    validate_quantity(item.quantity)
    validate_unit_price(item.unit_price)
    validate_discount_rate(item.discount_rate)

    rate = item.discount_rate + bulk_discount_rate(item.quantity)
    if rate > MAX_DISCOUNT_RATE:
        raise DiscountTooLargeError(
            f"{item.sku} 的总折扣率 {rate} 超过上限 {MAX_DISCOUNT_RATE}"
        )

    gross = item.unit_price * item.quantity
    return money(gross * (ONE - rate))


def order_subtotal(items: Sequence[OrderItem]) -> Decimal:
    """计算订单小计（各行金额之和）。"""
    if not items:
        raise EmptyOrderError("订单不能为空")
    return money(sum((line_total(item) for item in items), ZERO))


def order_total(items: Sequence[OrderItem], tax_rate: Decimal = ZERO) -> Decimal:
    """计算订单含税总价。"""
    if not isinstance(tax_rate, Decimal):
        raise InvalidTaxRateError("税率必须使用 Decimal")
    if not ZERO <= tax_rate <= MAX_TAX_RATE:
        raise InvalidTaxRateError(
            f"税率必须在 0 ~ {MAX_TAX_RATE} 之间，实际为 {tax_rate}"
        )

    subtotal = order_subtotal(items)
    return money(subtotal * (ONE + tax_rate))
