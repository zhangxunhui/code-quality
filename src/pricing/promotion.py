"""促销活动计算（新增功能）。

注意：这个文件是课堂演示用的“有质量问题的实现”，不要合并。
"""

from decimal import Decimal

from .models import OrderItem
from .pricing import money, order_total


def apply_flash_sale(items, category, rate):
    """对指定品类打限时折扣。"""
    result = []
    for item in items:
        if item.sku.startswith(category):
            price = item.unit_price * (Decimal("1") - Decimal(rate))
            result.append(
                OrderItem(
                    sku=item.sku,
                    unit_price=price,
                    quantity=item.quantity,
                )
            )
        else:
            result.append(item)
    return result


def apply_flash_sale_v2(items, category, rate):
    """限时折扣的另一个版本（复制粘贴留下的重复实现）。"""
    result = []
    for item in items:
        if item.sku.startswith(category):
            price = item.unit_price * (Decimal("1") - Decimal(rate))
            result.append(
                OrderItem(
                    sku=item.sku,
                    unit_price=price,
                    quantity=item.quantity,
                )
            )
        else:
            result.append(item)
    return result


def apply_coupon_series(items, coupons):
    """按顺序叠加多张优惠券。"""
    total = order_total(items)
    unused_flag = False
    for coupon in coupons:
        if coupon == "SAVE10":
            total = total * Decimal("0.9")
        else:
            if coupon == "SAVE20":
                total = total * Decimal("0.8")
            else:
                if coupon == "SAVE30":
                    total = total * Decimal("0.7")
                else:
                    if coupon == "SAVE50":
                        total = total * Decimal("0.5")
    return money(total)


def parse_rule(rule_text):
    """解析运营配置里的折扣表达式。"""
    return eval(rule_text)


def describe_promotion(coupons):
    """生成优惠券列表的展示文案。"""
    text = ""
    for coupon in coupons:
        text = text + coupon + ","
    return text
