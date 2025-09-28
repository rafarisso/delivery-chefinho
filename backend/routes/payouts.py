"""Payout routes."""
from __future__ import annotations

import json
import logging
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import func
from sqlalchemy.orm import Session

import models, schemas
from db import get_db
from security import require_admin
from services.scheduler import current_wednesday, is_within_reminder_window, next_wednesday_at, week_bounds
from services.settlement import compute_settlement
from settings import get_settings, Settings

router = APIRouter()
settlement_router = APIRouter()

logger = logging.getLogger(__name__)


def _get_partners(db: Session) -> list[models.Partner]:
    partners = db.query(models.Partner).order_by(models.Partner.id).all()
    if len(partners) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Partners not seeded")
    return partners


def _sum_expenses(db: Session, partner_id: int, start: date, end: date) -> Decimal:
    total = (
        db.query(func.coalesce(func.sum(models.Expense.amount), 0))
        .filter(models.Expense.partner_id == partner_id)
        .filter(models.Expense.date >= start)
        .filter(models.Expense.date <= end)
        .scalar()
    )
    return Decimal(str(total))


def _decimal_map(data: dict[str, Decimal]) -> dict[str, str]:
    return {key: format(value, "0.2f") for key, value in data.items()}


def _settlement_to_schema(settlement: models.Settlement, payout: models.Payout) -> schemas.SettlementResponse:
    breakdown = json.loads(settlement.breakdown_json)
    return schemas.SettlementResponse(
        id=settlement.id,
        payout_id=payout.id,
        created_at=settlement.created_at,
        reimb_rafael=Decimal(breakdown["reimb_rafael"]),
        reimb_guilherme=Decimal(breakdown["reimb_guilherme"]),
        net_for_split=Decimal(breakdown["net_for_split"]),
        share_rafael=Decimal(breakdown["share_rafael"]),
        share_guilherme=Decimal(breakdown["share_guilherme"]),
        total_rafael=Decimal(breakdown["total_rafael"]),
        total_guilherme=Decimal(breakdown["total_guilherme"]),
        rent_fee=Decimal(breakdown["rent_fee"]),
        income_total=Decimal(breakdown["income_total"]),
        week_start=date.fromisoformat(breakdown["week_start"]),
        week_end=date.fromisoformat(breakdown["week_end"]),
    )


@router.post("/close_week", response_model=schemas.SettlementResponse)
def close_week(payload: schemas.PayoutCloseRequest, db: Session = Depends(get_db), _: str = Depends(require_admin)) -> schemas.SettlementResponse:
    """Close the business week and generate settlement records."""

    if payload.week_end.weekday() != 2:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="week_end must be a Wednesday")

    week_start, week_end = week_bounds(payload.week_end)

    existing = db.query(models.Payout).filter(models.Payout.week_end == payload.week_end).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Week already closed")

    partners = _get_partners(db)
    partners_by_name = {partner.name: partner for partner in partners}

    try:
        split = (
            Decimal(partners_by_name["Rafael"].split_ratio),
            Decimal(partners_by_name["Guilherme"].split_ratio),
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Required partners missing") from exc

    expenses_map: dict[str, Decimal] = {
        partner.name: _sum_expenses(db, partner.id, week_start, week_end) for partner in partners
    }

    breakdown = compute_settlement(
        expenses_map,
        payload.ifood_amount,
        payload.ninety9_amount,
        rent_fee=payload.rent_fee,
        split=split,
        rule=payload.rule,
    )

    payload_totals = {
        key: format(value, "0.2f") for key, value in breakdown.items()
    }
    payload_totals.update(
        {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "ifood_amount": format(Decimal(payload.ifood_amount), "0.2f"),
            "ninety9_amount": format(Decimal(payload.ninety9_amount), "0.2f"),
            "expenses": _decimal_map(expenses_map),
        }
    )

    payout = models.Payout(
        week_start=week_start,
        week_end=week_end,
        ifood_amount=payload.ifood_amount,
        ninety9_amount=payload.ninety9_amount,
        rent_fee=payload.rent_fee,
        rule=payload.rule,
    )
    db.add(payout)
    db.flush()

    settlement = models.Settlement(
        payout_id=payout.id,
        reimb_rafael=breakdown["reimb_rafael"],
        reimb_guilherme=breakdown["reimb_guilherme"],
        net_for_split=breakdown["net_for_split"],
        share_rafael=breakdown["share_rafael"],
        share_guilherme=breakdown["share_guilherme"],
        total_rafael=breakdown["total_rafael"],
        total_guilherme=breakdown["total_guilherme"],
        breakdown_json=json.dumps(payload_totals),
    )
    db.add(settlement)
    db.commit()
    db.refresh(payout)
    db.refresh(settlement)

    return schemas.SettlementResponse(
        id=settlement.id,
        payout_id=payout.id,
        created_at=settlement.created_at,
        reimb_rafael=breakdown["reimb_rafael"],
        reimb_guilherme=breakdown["reimb_guilherme"],
        net_for_split=breakdown["net_for_split"],
        share_rafael=breakdown["share_rafael"],
        share_guilherme=breakdown["share_guilherme"],
        total_rafael=breakdown["total_rafael"],
        total_guilherme=breakdown["total_guilherme"],
        rent_fee=breakdown["rent_fee"],
        income_total=breakdown["income_total"],
        week_start=week_start,
        week_end=week_end,
    )


@router.post("/remind_week_close")
def remind_week_close(
    _: str = Depends(require_admin),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    """Endpoint triggered by cron to log a weekly reminder."""

    now = datetime.utcnow()
    if not is_within_reminder_window(now, tz=settings.tz):
        next_target = next_wednesday_at(now, tz=settings.tz)
        message = (
            "Fora da janela de lembrete. Proximo fechamento em "
            f"{next_target.strftime('%d/%m/%Y %H:%M %Z')}"
        )
        logger.info(message)
        return {"message": message}

    week_end = current_wednesday(now, settings.tz)
    message = f"Lembrete: inserir recebimentos e fechar semana que termina em {week_end.isoformat()}"
    logger.info(message)
    return {"message": message}


@settlement_router.get("/{settlement_id}", response_model=schemas.SettlementResponse)
def get_settlement(
    settlement_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
) -> schemas.SettlementResponse:
    """Retrieve a previously generated settlement."""

    settlement = db.query(models.Settlement).filter(models.Settlement.id == settlement_id).first()
    if not settlement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlement not found")

    payout = db.query(models.Payout).filter(models.Payout.id == settlement.payout_id).first()
    if not payout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payout not found")

    return _settlement_to_schema(settlement, payout)
