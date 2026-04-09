import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.base import BaseAdapter
from app.core.constants import JobStatus
from app.core.logging import get_logger
from app.db.repositories import jobs as jobs_repo
from app.db.repositories import task_runs as task_runs_repo
from app.schemas.domain.raw_record import RawRecord
from app.services.artifact_service import store_raw_html

logger = get_logger(__name__)


async def run_ingest(
    session: AsyncSession,
    *,
    adapter: BaseAdapter,
    job_id: uuid.UUID,
    url: str,
    **fetch_kwargs,
) -> tuple[uuid.UUID, list[RawRecord], bool]:
    """Ingest pipeline: create task run, fetch HTML, store artifact, parse.

    Returns (task_run_id, raw_records, is_duplicate_html).
    """
    await jobs_repo.update_job_status(session, job_id, status=JobStatus.RUNNING)

    task_run = await task_runs_repo.create_task_run(
        session,
        job_id=job_id,
        task_name=f"ingest_{adapter.source}",
    )

    raw_html = await adapter.fetch(url, **fetch_kwargs)

    artifact_id, is_duplicate = await store_raw_html(
        session,
        task_run_id=task_run.id,
        html=raw_html,
        source=adapter.source,
        url=url,
    )

    raw_records = adapter.parse(raw_html)

    logger.info(
        "ingest_complete",
        job_id=str(job_id),
        task_run_id=str(task_run.id),
        raw_count=len(raw_records),
        is_duplicate=is_duplicate,
    )

    return task_run.id, raw_records, is_duplicate
