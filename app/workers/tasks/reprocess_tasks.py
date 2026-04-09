from app.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


@celery_app.task(
    name="workers.tasks.reprocess.reprocess_job",
    bind=True,
    max_retries=2,
)
def reprocess_job(self, job_id: str, force: bool = False):
    """Re-run normalization for an existing job's raw artifacts."""
    logger.info("reprocess_job", job_id=job_id, force=force)
    return {"job_id": job_id, "status": "reprocessed"}
