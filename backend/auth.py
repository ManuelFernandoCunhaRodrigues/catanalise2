import hmac
import os

from fastapi import Header, HTTPException


def get_api_token() -> str | None:
    token = os.getenv("API_AUTH_TOKEN", "").strip()
    return token or None


async def require_api_token(
    authorization: str | None = Header(default=None),
    x_api_token: str | None = Header(default=None),
) -> None:
    configured_token = get_api_token()
    if not configured_token:
        return

    bearer_token = _extract_bearer_token(authorization)
    provided_token = x_api_token or bearer_token

    if not provided_token or not hmac.compare_digest(provided_token, configured_token):
        raise HTTPException(status_code=401, detail="Token de autenticacao invalido ou ausente.")


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    prefix = "Bearer "
    if authorization.startswith(prefix):
        return authorization[len(prefix) :].strip() or None

    return None
