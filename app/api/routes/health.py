from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.api.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "unknown"
    redis_status = "unknown"

    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    try:
        from redis import Redis

        from app.core.config import get_settings

        settings = get_settings()
        r = Redis.from_url(settings.redis_url, socket_connect_timeout=2)
        r.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "error"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"

    return HealthResponse(status=overall, database=db_status, redis=redis_status)
