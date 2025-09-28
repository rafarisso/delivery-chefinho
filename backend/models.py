"""Database models."""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from db import Base


class Partner(Base):
    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    split_ratio = Column(Numeric(5, 4), nullable=False, default=Decimal("0.5"))

    expenses = relationship("Expense", back_populates="partner", cascade="all, delete-orphan")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    partner_id = Column(Integer, ForeignKey("partners.id"), nullable=False, index=True)
    note = Column(String(255), nullable=True)
    platform = Column(String(50), nullable=True)
    category = Column(String(50), nullable=True)
    receipt_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    partner = relationship("Partner", back_populates="expenses")


class Payout(Base):
    __tablename__ = "payouts"
    __table_args__ = (UniqueConstraint("week_end", name="uq_payout_week_end"),)

    id = Column(Integer, primary_key=True, index=True)
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False, index=True)
    ifood_amount = Column(Numeric(12, 2), nullable=False)
    ninety9_amount = Column(Numeric(12, 2), nullable=False)
    rent_fee = Column(Numeric(12, 2), nullable=False, default=Decimal("50.00"))
    rule = Column(String(32), nullable=False, default="rent_before_split")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    settlement = relationship("Settlement", back_populates="payout", uselist=False, cascade="all, delete-orphan")


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True)
    payout_id = Column(Integer, ForeignKey("payouts.id"), nullable=False, unique=True)
    reimb_rafael = Column(Numeric(12, 2), nullable=False)
    reimb_guilherme = Column(Numeric(12, 2), nullable=False)
    net_for_split = Column(Numeric(12, 2), nullable=False)
    share_rafael = Column(Numeric(12, 2), nullable=False)
    share_guilherme = Column(Numeric(12, 2), nullable=False)
    total_rafael = Column(Numeric(12, 2), nullable=False)
    total_guilherme = Column(Numeric(12, 2), nullable=False)
    breakdown_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    payout = relationship("Payout", back_populates="settlement")
