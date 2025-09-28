"""Tests for settlement computation."""
from decimal import Decimal

import pytest

from services.settlement import compute_settlement


@pytest.mark.parametrize(
    "expenses, ifood, ninety9, expected_rafael, expected_guilherme",
    [
        ({"Rafael": Decimal("500"), "Guilherme": Decimal("0")}, Decimal("500"), Decimal("500"), Decimal("775.00"), Decimal("225.00")),
    ],
)
def test_compute_settlement_base_case(expenses, ifood, ninety9, expected_rafael, expected_guilherme):
    result = compute_settlement(expenses, ifood, ninety9)
    assert result["total_rafael"] == expected_rafael
    assert result["total_guilherme"] == expected_guilherme
    assert result["net_for_split"] == Decimal("450.00")


def test_compute_settlement_no_expenses():
    result = compute_settlement({}, Decimal("1000"), Decimal("500"))
    assert result["reimb_rafael"] == Decimal("0.00")
    assert result["reimb_guilherme"] == Decimal("0.00")
    assert result["net_for_split"] == Decimal("1450.00")
    assert result["total_rafael"] == Decimal("775.00")
    assert result["total_guilherme"] == Decimal("725.00")


def test_compute_settlement_negative_net():
    result = compute_settlement({"Rafael": Decimal("800"), "Guilherme": Decimal("200")}, Decimal("500"), Decimal("100"))
    assert result["net_for_split"] == Decimal("-450.00")
    assert result["total_rafael"] == Decimal("625.00")
    assert result["total_guilherme"] == Decimal("-25.00")
