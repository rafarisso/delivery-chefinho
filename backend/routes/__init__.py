"""API router aggregation."""
from fastapi import APIRouter

from . import auth, expenses, payouts, reports

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["expenses"])
api_router.include_router(payouts.router, prefix="/payouts", tags=["payouts"])
api_router.include_router(payouts.settlement_router, prefix="/settlements", tags=["settlements"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
