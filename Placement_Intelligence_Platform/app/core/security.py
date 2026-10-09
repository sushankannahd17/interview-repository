import hmac

from fastapi import Header, HTTPException, status

from app.core.config import settings


async def require_internal_api_key(x_internal_api_key: str | None = Header(default=None)) -> None:
    expected = settings.internal_api_key
    if not x_internal_api_key or not expected or not hmac.compare_digest(x_internal_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key",
        )
