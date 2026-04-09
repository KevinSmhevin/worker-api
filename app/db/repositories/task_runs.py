import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import TaskRunStatus
from app.db.models.task_run import TaskRun


async def create_task_run(
    session: AsyncSession,
    *,
    job_id: uuid.UUID,
    task_name: str,
    attempt: int = 1,
) -> TaskRun:
    task_run = TaskRun(
        job_id=job_id,
        task_name=task_name,
        status=TaskRunStatus.RUNNING,
        attempt=attempt,
        started_at=datetime.now(timezone.utc),
    )
    session.add(task_run)
    await session.flush()
    return task_run


async def mark_task_run_success(
    session: AsyncSession,
    task_run_id: uuid.UUID,
) -> TaskRun | None:
    task_run = await session.get(TaskRun, task_run_id)
    if not task_run:
        return None
    task_run.status = TaskRunStatus.SUCCESS
    task_run.finished_at = datetime.now(timezone.utc)
    await session.flush()
    return task_run


async def mark_task_run_failed(
    session: AsyncSession,
    task_run_id: uuid.UUID,
    *,
    error_message: str,
) -> TaskRun | None:
    task_run = await session.get(TaskRun, task_run_id)
    if not task_run:
        return None
    task_run.status = TaskRunStatus.FAILED
    task_run.error_message = error_message
    task_run.finished_at = datetime.now(timezone.utc)
    await session.flush()
    return task_run


async def get_task_runs_for_job(
    session: AsyncSession,
    job_id: uuid.UUID,
) -> list[TaskRun]:
    stmt = (
        select(TaskRun)
        .where(TaskRun.job_id == job_id)
        .order_by(TaskRun.created_at.desc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
