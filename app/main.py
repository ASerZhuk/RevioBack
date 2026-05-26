from fastapi import FastAPI
from sqlalchemy import text

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.history import router as history_router
from app.api.tokens import router as tokens_router
from app.core.config import settings
from app.db.session import engine


app = FastAPI(title=settings.app_name)


@app.on_event("startup")
async def ensure_analysis_history_product_price_column() -> None:
    async with engine.begin() as conn:
        result = await conn.execute(text("PRAGMA table_info(analysis_history)"))
        columns = {row[1] for row in result.fetchall()}

        if "product_price" not in columns:
            await conn.execute(
                text("ALTER TABLE analysis_history ADD COLUMN product_price VARCHAR(128)")
            )

app.include_router(auth_router)
app.include_router(health_router)
app.include_router(history_router)
app.include_router(tokens_router)
