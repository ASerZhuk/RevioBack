from typing import Any

import anyio
from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings


def _verify_google_id_token(token: str) -> dict[str, Any]:
    client_ids = [settings.google_client_id, settings.google_android_client_id]
    last_error: ValueError | None = None

    for client_id in [value for value in client_ids if value]:
        try:
            return id_token.verify_oauth2_token(token, requests.Request(), client_id)
        except ValueError as error:
            last_error = error

    raise last_error or ValueError("Google client id is not configured")


async def verify_google_id_token(token: str) -> tuple[str, str] | None:
    try:
        payload = await anyio.to_thread.run_sync(_verify_google_id_token, token)
    except ValueError:
        return None

    google_sub = payload.get("sub")
    email = payload.get("email")
    is_email_verified = payload.get("email_verified")
    if not isinstance(google_sub, str) or not isinstance(email, str) or not is_email_verified:
        return None

    return email, google_sub
