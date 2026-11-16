"""历史遗留折扣接口的适配层（重构后：复用统一的 pricing 模块）。"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from .models import OrderItem
from .pricing import ONE, ZERO, money, order_total

# 优惠券折扣率集中管理，新增券种只改这里。
COUPON_RATES: dict[str, Decimal] = {
    "SAVE10": Decimal("0.10"),
    "SAVE20": Decimal("0.20"),
    "SAVE30": Decimal("0.30"),
}


def _parse_amount(value: Any, field: str) -> Decimal:
    """把旧系统里的字符串金额转换为 Decimal。"""
    try:
        amount = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"{field} 不是合法数字：{value!r}") from exc
    return amount


def _to_item(raw: dict[str, Any]) -> OrderItem:
    """把旧系统的字典结构转换为 OrderItem。"""
    return OrderItem(
        sku=str(raw["sku"]),
        unit_price=_parse_amount(raw["price"], "price"),
        quantity=int(raw["qty"]),
    )


def calculate(items: list[dict[str, Any]]) -> Decimal:
    """计算订单金额，复用统一的折扣与四舍五入规则。"""
    return order_total([_to_item(raw) for raw in items])


def apply_coupon(total: Decimal, coupon: str | None) -> Decimal:
    """在订单总额上叠加优惠券折扣。"""
    rate = COUPON_RATES.get(coupon or "", ZERO)
    return money(total * (ONE - rate))
