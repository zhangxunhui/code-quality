"""把用户输入（字符串）解析为可用于计算的数值。"""

from decimal import Decimal, InvalidOperation

from .errors import InvalidPriceError, InvalidQuantityError
from .pricing import validate_quantity, validate_unit_price


def parse_price(raw: str) -> Decimal:
    """把字符串解析为单价。

    Raises:
        InvalidPriceError: 输入不是合法数字、不是有限值，或不为正数。
    """
    text = raw.strip()
    try:
        value = Decimal(text)
    except InvalidOperation as exc:
        raise InvalidPriceError(f"无法解析价格：{raw!r}") from exc
    if not value.is_finite():
        raise InvalidPriceError(f"价格必须是有限数值：{raw!r}")
    validate_unit_price(value)
    return value


def parse_quantity(raw: str) -> int:
    """把字符串解析为购买数量。

    Raises:
        InvalidQuantityError: 输入不是整数，或不为正数。
    """
    try:
        value = int(raw.strip())
    except ValueError as exc:
        raise InvalidQuantityError(f"无法解析数量：{raw!r}") from exc
    validate_quantity(value)
    return value
