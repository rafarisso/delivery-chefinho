"""Settlement calculation service."""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Tuple

TWOPLACES = Decimal("0.01")


def _to_decimal(value: Decimal | float | int | str) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def compute_settlement(
    expenses_by_partner: Dict[str, Decimal | float | int | str],
    ifood_amount: Decimal | float | int | str,
    ninety9_amount: Decimal | float | int | str,
    rent_fee: Decimal | float | int | str = Decimal("50.00"),
    split: Tuple[Decimal | float | int | str, Decimal | float | int | str] = (Decimal("0.5"), Decimal("0.5")),
    rule: str = "rent_before_split",
) -> Dict[str, Decimal]:
    """Compute settlement amounts for the partners.

    Returns a breakdown with all intermediate values quantised to two decimal places.
    """

    rent_fee_dec = _to_decimal(rent_fee)
    split_rafael = _to_decimal(split[0])
    split_guilherme = _to_decimal(split[1])

    income_total = _to_decimal(ifood_amount) + _to_decimal(ninety9_amount)
    reimb_rafael = _to_decimal(expenses_by_partner.get("Rafael", Decimal()))
    reimb_guilherme = _to_decimal(expenses_by_partner.get("Guilherme", Decimal()))

    if rule == "rent_before_split":
        net_for_split = income_total - reimb_rafael - reimb_guilherme - rent_fee_dec
        share_rafael = net_for_split * split_rafael
        share_guilherme = net_for_split * split_guilherme
        total_rafael = reimb_rafael + rent_fee_dec + share_rafael
        total_guilherme = reimb_guilherme + share_guilherme
    elif rule == "rent_after_split":
        net_for_split = income_total - reimb_rafael - reimb_guilherme
        share_rafael = net_for_split * split_rafael
        share_guilherme = net_for_split * split_guilherme
        total_rafael = reimb_rafael + share_rafael + rent_fee_dec
        total_guilherme = reimb_guilherme + share_guilherme
    else:
        raise ValueError(f"Unsupported rule: {rule}")

    return {
        "rent_fee": _quantize(rent_fee_dec),
        "income_total": _quantize(income_total),
        "reimb_rafael": _quantize(reimb_rafael),
        "reimb_guilherme": _quantize(reimb_guilherme),
        "net_for_split": _quantize(net_for_split),
        "share_rafael": _quantize(share_rafael),
        "share_guilherme": _quantize(share_guilherme),
        "total_rafael": _quantize(total_rafael),
        "total_guilherme": _quantize(total_guilherme),
    }
