import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.config import router as config_router
from app.api.errors import router as errors_router
from app.api.health import router as health_router
from app.api.history import router as history_router
from app.api.tokens import router as tokens_router
from app.core.config import settings
from app.core.telegram import notify_error
from app.db.seed import seed_default_config
from app.db.session import AsyncSessionLocal, engine

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)


@app.middleware("http")
async def catch_unhandled_exceptions(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        tb = traceback.format_exc()
        logger.error("Unhandled error: %s", tb)
        await notify_error(
            source="backend",
            error_type=type(exc).__name__,
            message=str(exc),
            context=tb[-1000:],
        )
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.on_event("startup")
async def startup() -> None:
    # Ensure product_price column exists (legacy migration guard)
    async with engine.begin() as conn:
        result = await conn.execute(text("PRAGMA table_info(analysis_history)"))
        columns = {row[1] for row in result.fetchall()}
        if "product_price" not in columns:
            await conn.execute(
                text("ALTER TABLE analysis_history ADD COLUMN product_price VARCHAR(128)")
            )

    # Seed default config values
    async with AsyncSessionLocal() as session:
        await seed_default_config(session)


app.include_router(auth_router)
app.include_router(health_router)
app.include_router(history_router)
app.include_router(tokens_router)
app.include_router(config_router)
app.include_router(errors_router)
app.include_router(admin_router)

# Serve admin panel at /admin
import os
_static_dir = os.path.join(os.path.dirname(__file__), "..", "static", "admin")
if os.path.isdir(_static_dir):
    app.mount("/admin", StaticFiles(directory=_static_dir, html=True), name="admin")
