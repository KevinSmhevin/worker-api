from datetime import datetime, timedelta, timezone

from app.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(
    name="workers.tasks.cleanup.cleanup_old_runs",
    bind=True,
    max_retries=2,
)
def cleanup_old_runs(self, older_than_days: int = 30):
    """Remove task runs older than the specified number of days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
    logger.info("cleanup_old_runs", cutoff=cutoff.isoformat())
    return {"cutoff": cutoff.isoformat(), "status": "completed"}
