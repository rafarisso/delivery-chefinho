"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status

from schemas import AuthRequest, TokenResponse
from settings import get_settings, Settings

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: AuthRequest, settings: Settings = Depends(get_settings)) -> TokenResponse:
    """Simple ADMIN_TOKEN based authentication."""

    if not settings.admin_token:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Authentication not configured yet")

    if payload.password != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return TokenResponse(access_token=settings.admin_token)
