import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import JobStatus
from app.core.logging import get_logger
from app.db.repositories import jobs as jobs_repo
from app.db.repositories import normalized_records as records_repo
from app.db.repositories import task_runs as task_runs_repo
from app.schemas.domain.normalized_record import NormalizedRecordSchema

logger = get_logger(__name__)


async def run_persist(
    session: AsyncSession,
    *,
    job_id: uuid.UUID,
    task_run_id: uuid.UUID,
    records: list[NormalizedRecordSchema],
) -> int:
    """Persist pipeline: write normalized records to DB and update job status.

    Returns the number of records persisted.
    """
    if not records:
        await task_runs_repo.mark_task_run_success(session, task_run_id)
        await jobs_repo.update_job_status(
            session, job_id, status=JobStatus.COMPLETED
        )
        logger.info("persist_no_new_records", job_id=str(job_id))
        return 0

    record_dicts = [r.model_dump() for r in records]
    await records_repo.bulk_create_normalized_records(session, record_dicts)

    await task_runs_repo.mark_task_run_success(session, task_run_id)
    await jobs_repo.update_job_status(session, job_id, status=JobStatus.COMPLETED)

    logger.info(
        "persist_complete",
        job_id=str(job_id),
        persisted_count=len(records),
    )

    return len(records)
