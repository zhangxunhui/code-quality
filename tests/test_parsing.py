"""用户输入解析的单元测试。"""

from decimal import Decimal

import pytest

from pricing import InvalidPriceError, InvalidQuantityError, parse_price, parse_quantity


class TestParsePrice:
    def test_parses_plain_decimal(self) -> None:
        assert parse_price("19.99") == Decimal("19.99")

    def test_strips_surrounding_whitespace(self) -> None:
        assert parse_price("  19.99  ") == Decimal("19.99")

    @pytest.mark.parametrize("raw", ["", "   ", "abc", "12,5"])
    def test_rejects_garbage(self, raw: str) -> None:
        with pytest.raises(InvalidPriceError, match="无法解析"):
            parse_price(raw)

    @pytest.mark.parametrize("raw", ["NaN", "Infinity", "-Infinity"])
    def test_rejects_non_finite_values(self, raw: str) -> None:
        with pytest.raises(InvalidPriceError, match="有限数值"):
            parse_price(raw)

    @pytest.mark.parametrize("raw", ["0", "-1"])
    def test_rejects_non_positive_values(self, raw: str) -> None:
        with pytest.raises(InvalidPriceError, match="必须大于 0"):
            parse_price(raw)


class TestParseQuantity:
    def test_parses_integer(self) -> None:
        assert parse_quantity("3") == 3

    def test_strips_surrounding_whitespace(self) -> None:
        assert parse_quantity(" 3 ") == 3

    @pytest.mark.parametrize("raw", ["", "abc", "3.5"])
    def test_rejects_non_integer(self, raw: str) -> None:
        with pytest.raises(InvalidQuantityError, match="无法解析"):
            parse_quantity(raw)

    @pytest.mark.parametrize("raw", ["0", "-2"])
    def test_rejects_non_positive(self, raw: str) -> None:
        with pytest.raises(InvalidQuantityError, match="必须大于 0"):
            parse_quantity(raw)
