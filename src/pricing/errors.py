"""价格计算模块的异常类型。"""


class PricingError(Exception):
    """价格计算相关异常的基类。"""


class InvalidPriceError(PricingError):
    """单价格式非法或不为正数。"""


class InvalidQuantityError(PricingError):
    """购买数量非法。"""


class InvalidDiscountRateError(PricingError):
    """折扣率超出允许范围。"""


class DiscountTooLargeError(PricingError):
    """折扣率叠加后超过上限。"""


class InvalidTaxRateError(PricingError):
    """税率超出允许范围。"""


class EmptyOrderError(PricingError):
    """订单中没有任何商品。"""
