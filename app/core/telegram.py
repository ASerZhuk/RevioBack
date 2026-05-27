import json
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def _get_tg_settings() -> tuple[str | None, str | None]:
    """Read bot_token and chat_id from app_config table; fall back to .env values."""
    token = settings.telegram_bot_token
    chat = settings.telegram_chat_id
    try:
        from app.db.session import AsyncSessionLocal
        from app.models.app_config import AppConfig
        async with AsyncSessionLocal() as session:
            enabled_row = await session.get(AppConfig, "telegram.enabled")
            if enabled_row:
                enabled = json.loads(enabled_row.value)
                if not enabled:
                    return None, None

            token_row = await session.get(AppConfig, "telegram.bot_token")
            chat_row = await session.get(AppConfig, "telegram.chat_id")
            if token_row:
                v = json.loads(token_row.value)
                if v:
                    token = v
            if chat_row:
                v = json.loads(chat_row.value)
                if v:
                    chat = v
    except Exception as exc:
        logger.debug("Could not read telegram settings from DB: %s", exc)
    return token, chat


async def send_telegram(message: str) -> None:
    token, chat = await _get_tg_settings()
    if not token or not chat:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        proxy = settings.telegram_proxy_url or None
        async with httpx.AsyncClient(timeout=10, proxy=proxy) as client:
            await client.post(url, json={
                "chat_id": chat,
                "text": message[:4096],
                "parse_mode": "HTML",
            })
    except Exception as exc:
        logger.warning("Telegram notification failed: %s", exc, exc_info=True)


async def notify_error(source: str, error_type: str, message: str, context: str | None = None) -> None:
    text = (
        f"🚨 <b>Ошибка [{source}]</b>\n"
        f"<b>Тип:</b> {error_type}\n"
        f"<b>Сообщение:</b> {message}"
    )
    if context:
        text += f"\n<b>Контекст:</b> <code>{context[:500]}</code>"
    await send_telegram(text)
