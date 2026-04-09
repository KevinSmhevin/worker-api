import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import JobStatus
from app.db.models.job import Job


async def create_job(
    session: AsyncSession,
    *,
    job_type: str,
    payload: dict | None = None,
) -> Job:
    job = Job(type=job_type, status=JobStatus.PENDING, payload=payload)
    session.add(job)
    await session.flush()
    return job


async def get_job(session: AsyncSession, job_id: uuid.UUID) -> Job | None:
    return await session.get(Job, job_id)


async def list_jobs(
    session: AsyncSession,
    *,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Job]:
    stmt = select(Job).order_by(Job.created_at.desc()).limit(limit).offset(offset)
    if status:
        stmt = stmt.where(Job.status == status)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def update_job_status(
    session: AsyncSession,
    job_id: uuid.UUID,
    *,
    status: str,
    error_message: str | None = None,
) -> Job | None:
    job = await get_job(session, job_id)
    if not job:
        return None
    job.status = status
    if error_message is not None:
        job.error_message = error_message
    await session.flush()
    return job
