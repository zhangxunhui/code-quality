"""价格计算使用的数据模型。"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class OrderItem:
    """订单中的一行商品。

    Attributes:
        sku: 商品编号。
        unit_price: 单价，使用 Decimal 以避免浮点误差。
        quantity: 购买数量，必须为正整数。
        discount_rate: 该行商品的额外折扣率，取值范围 0 ~ 0.5。
    """

    sku: str
    unit_price: Decimal
    quantity: int
    discount_rate: Decimal = Decimal("0")
