from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.core.config import settings


def require_api_key(x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None) -> str:
    if settings.is_production and not settings.secret_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"error": {"code": "missing_server_secret", "message": "API authentication is not configured.", "details": []}})
    if not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": {"code": "missing_api_key", "message": "API key required.", "details": []}})
    expected = settings.secret_key
    if x_api_key != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": {"code": "invalid_api_key", "message": "Invalid API key.", "details": []}})
    return x_api_key


ApiKeyDep = Depends(require_api_key)
