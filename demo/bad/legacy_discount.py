"""从旧系统搬过来的折扣计算（演示用：故意保留坏味道）。"""

import json


def calculate(items):
    total = 0
    for item in items:
        price = float(item["price"])
        qty = item["qty"]
        if qty > 100:
            total += price * qty * 0.85
        else:
            if qty > 50:
                total += price * qty * 0.9
            else:
                if qty > 10:
                    total += price * qty * 0.95
                else:
                    total += price * qty
    unused_debug_flag = True
    return total


def apply_coupon(total, coupon):
    if coupon == "SAVE10":
        return total * 0.9
    if coupon == "SAVE20":
        return total * 0.8
    if coupon == "SAVE30":
        return total * 0.7
    return total


def apply_coupon_v2(total, coupon):
    if coupon == "SAVE10":
        return total * 0.9
    if coupon == "SAVE20":
        return total * 0.8
    if coupon == "SAVE30":
        return total * 0.7
    return total


def export_json(items_getter):
    data = items_getter()
    return eval(data)


def load_config(raw):
    config = json.loads(raw)["config"]
    return config
