"""Reporting routes."""
from __future__ import annotations

import csv
import io
import json
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import models, schemas
from db import get_db
from security import require_admin

router = APIRouter()


def _deserialize_settlement(settlement: models.Settlement, payout: models.Payout) -> schemas.SettlementResponse:
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


def _get_settlement_by_week_end(db: Session, week_end: date) -> tuple[models.Settlement, models.Payout, dict[str, str]]:
    payout = db.query(models.Payout).filter(models.Payout.week_end == week_end).first()
    if not payout or not payout.settlement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settlements not found for week")
    settlement = payout.settlement
    breakdown = json.loads(settlement.breakdown_json)
    return settlement, payout, breakdown


@router.get("/settlements", response_model=list[schemas.SettlementResponse])
def list_settlements(db: Session = Depends(get_db), _: str = Depends(require_admin)) -> list[schemas.SettlementResponse]:
    """Return all settlements ordered by week."""

    rows = (
        db.query(models.Settlement, models.Payout)
        .join(models.Payout, models.Settlement.payout_id == models.Payout.id)
        .order_by(models.Payout.week_end.desc())
        .all()
    )
    return [_deserialize_settlement(settlement, payout) for settlement, payout in rows]


@router.get("/weekly.csv")
def weekly_csv(
    week_end: date = Query(..., description="Quarta-feira de fechamento", alias="week_end"),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
) -> Response:
    """Export settlement summary as CSV."""

    _, payout, breakdown = _get_settlement_by_week_end(db, week_end)

    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    writer.writerow(["Periodo", breakdown["week_start"], breakdown["week_end"]])
    writer.writerow(["Recebido iFood", breakdown.get("ifood_amount", "0.00")])
    writer.writerow(["Recebido 99 Food", breakdown.get("ninety9_amount", "0.00")])
    writer.writerow(["Receita total", breakdown["income_total"]])
    writer.writerow(["Aluguel", breakdown["rent_fee"]])
    writer.writerow([])
    expenses = breakdown.get("expenses", {})
    for name, value in expenses.items():
        writer.writerow([f"Despesas {name}", value])
    writer.writerow(["Saldo para divisao", breakdown.get("net_for_split")])
    writer.writerow([])
    writer.writerow(["Total Rafael", breakdown.get("total_rafael")])
    writer.writerow(["Total Guilherme", breakdown.get("total_guilherme")])
    writer.writerow(["Regra", payout.rule])

    csv_bytes = output.getvalue().encode("utf-8-sig")
    headers = {
        "Content-Disposition": f"attachment; filename=relatorio-{week_end.isoformat()}.csv"
    }
    return Response(content=csv_bytes, media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/weekly.pdf")
def weekly_pdf(
    week_end: date = Query(..., description="Quarta-feira de fechamento", alias="week_end"),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
) -> StreamingResponse:
    """Export settlement summary as a simple PDF."""

    _, payout, breakdown = _get_settlement_by_week_end(db, week_end)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setTitle(f"Relatorio Semana {week_end.isoformat()}")
    text = pdf.beginText(40, height - 80)
    text.setFont("Helvetica", 12)

    expenses = breakdown.get("expenses", {})

    lines = [
        "Hamburgueria do Cheffinho - Unidade 2",
        f"Relatorio semanal - fechamento {week_end.strftime('%d/%m/%Y')}",
        "",
        f"Periodo: {breakdown['week_start']} a {breakdown['week_end']}",
        f"Recebido iFood: R$ {breakdown.get('ifood_amount', '0.00')}",
        f"Recebido 99 Food: R$ {breakdown.get('ninety9_amount', '0.00')}",
        f"Receita total: R$ {breakdown['income_total']}",
        f"Aluguel: R$ {breakdown['rent_fee']}",
        "",
        f"Despesas Rafael: R$ {expenses.get('Rafael', breakdown['reimb_rafael'])}",
        f"Despesas Guilherme: R$ {expenses.get('Guilherme', breakdown['reimb_guilherme'])}",
        f"Saldo para divisao: R$ {breakdown['net_for_split']}",
        "",
        f"Total Rafael: R$ {breakdown['total_rafael']}",
        f"Total Guilherme: R$ {breakdown['total_guilherme']}",
        f"Regra aplicada: {payout.rule}",
    ]

    for line in lines:
        text.textLine(line)

    pdf.drawText(text)
    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    headers = {
        "Content-Disposition": f"attachment; filename=relatorio-{week_end.isoformat()}.pdf"
    }
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)
