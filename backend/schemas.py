# backend/schemas.py
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, ConfigDict

# Tipos numéricos com restrições (v2: Annotated + Field)
Money = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
PositiveMoney = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
Ratio = Annotated[Decimal, Field(ge=0, le=1, max_digits=5, decimal_places=4)]


class PartnerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    split_ratio: Ratio


class ExpenseCreate(BaseModel):
    date: date
    amount: PositiveMoney
    partner_name: Literal["Rafael", "Guilherme"]
    platform: Optional[str] = None
    category: Optional[str] = None
    note: Optional[str] = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date
    amount: Money
    partner_name: str
    platform: Optional[str] = None
    category: Optional[str] = None
    note: Optional[str] = None
    receipt_url: Optional[HttpUrl] = None
    created_at: datetime


class ExpensesSummary(BaseModel):
    rafael: Money
    guilherme: Money


class PayoutCloseRequest(BaseModel):
    week_end: date
    ifood_amount: Money
    ninety9_amount: Money
    rent_fee: Money = Decimal("50.00")
    rule: Literal["rent_before_split", "rent_after_split"] = "rent_before_split"


class SettlementBreakdown(BaseModel):
    reimb_rafael: Money
    reimb_guilherme: Money
    net_for_split: Money
    share_rafael: Money
    share_guilherme: Money
    total_rafael: Money
    total_guilherme: Money
    rent_fee: Money
    income_total: Money
    week_start: date
    week_end: date


class SettlementResponse(SettlementBreakdown):
    model_config = ConfigDict(from_attributes=True)
    id: int
    payout_id: int
    created_at: datetime


class AuthRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
