from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MarketPlaceParser API"
    database_url: str = "sqlite+aiosqlite:///./app.db"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 30
    google_client_id: str = "164747175175-l8r2aq2moiiiv1vkh933vjjv8f0di5de.apps.googleusercontent.com"
    google_android_client_id: str | None = None
    initial_user_tokens: int = 3
    telegram_bot_token: str | None = None
    telegram_chat_id: str | None = None
    telegram_proxy_url: str | None = None  # e.g. "socks5://user:pass@host:port" or "http://host:port"
    admin_secret: str = "change-admin-secret"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
