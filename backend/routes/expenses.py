"""Expense routes."""
from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

import models, schemas
from db import get_db
from security import require_admin
from services.storage import get_storage_service, StorageService

router = APIRouter()


def _parse_decimal(raw_value: str, field: str) -> Decimal:
    try:
        value = Decimal(raw_value)
    except (InvalidOperation, ValueError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid {field}") from None
    if value <= 0:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{field} must be greater than zero")
    return value


def _parse_date(raw_value: str, field: str) -> date:
    try:
        return date.fromisoformat(raw_value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"Invalid {field}") from exc


def _get_partner_by_name(db: Session, partner_name: str) -> models.Partner:
    partner = db.query(models.Partner).filter(models.Partner.name == partner_name).first()
    if not partner:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found")
    return partner


def _expense_to_schema(expense: models.Expense) -> schemas.ExpenseResponse:
    return schemas.ExpenseResponse(
        id=expense.id,
        date=expense.date,
        amount=Decimal(expense.amount),
        partner_name=expense.partner.name,
        platform=expense.platform,
        category=expense.category,
        note=expense.note,
        receipt_url=expense.receipt_url,
        created_at=expense.created_at,
    )


@router.post("", response_model=schemas.ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    file: UploadFile = File(...),
    amount: str = Form(...),
    date_value: str = Form(...),
    partner_name: str = Form(...),
    platform: str | None = Form(None),
    category: str | None = Form(None),
    note: str | None = Form(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
    storage: StorageService = Depends(get_storage_service),
) -> schemas.ExpenseResponse:
    """Create a new expense entry with receipt upload."""

    expense_amount = _parse_decimal(amount, "amount")
    expense_date = _parse_date(date_value, "date")
    partner = _get_partner_by_name(db, partner_name)

    iso_year, iso_week, _ = expense_date.isocalendar()
    suffix = Path(file.filename or "").suffix or ".jpg"
    destination = Path(f"{iso_year}/{iso_week:02d}/{uuid4().hex}{suffix.lower()}")

    try:
        receipt_url = storage.upload_receipt(file.file, destination, content_type=file.content_type)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    expense = models.Expense(
        date=expense_date,
        amount=expense_amount,
        partner_id=partner.id,
        platform=platform,
        category=category,
        note=note,
        receipt_url=receipt_url,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    return _expense_to_schema(expense)


@router.get("", response_model=List[schemas.ExpenseResponse])
def list_expenses(
    start: date | None = Query(None),
    end: date | None = Query(None),
    partner_name: str | None = Query(None),
    db: Session = Depends(get_db),
    _: str = Depends(require_admin),
) -> List[schemas.ExpenseResponse]:
    """List expenses with optional filters."""

    query = db.query(models.Expense).join(models.Partner)

    if start:
        query = query.filter(models.Expense.date >= start)
    if end:
        query = query.filter(models.Expense.date <= end)
    if partner_name:
        query = query.filter(models.Partner.name == partner_name)

    expenses = query.order_by(models.Expense.date.desc(), models.Expense.id.desc()).all()
    return [_expense_to_schema(expense) for expense in expenses]
