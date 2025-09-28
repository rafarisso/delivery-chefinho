"""Security dependencies for API protection."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from settings import get_settings, Settings

_security = HTTPBearer(auto_error=False)


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
    settings: Settings = Depends(get_settings),
) -> str:
    """Validate Bearer token against ADMIN_TOKEN when configured."""

    if not settings.admin_token:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="ADMIN_TOKEN not configured")

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")

    token = credentials.credentials
    if token != settings.admin_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return "admin"
