import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.celery_app import celery_app
from app.core.constants import JobStatus
from app.db.repositories import jobs as jobs_repo
from app.schemas.api.jobs import JobCreate, JobListResponse, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=202)
async def create_job(body: JobCreate, db: AsyncSession = Depends(get_db)):
    job = await jobs_repo.create_job(
        db,
        job_type=body.type,
        payload=body.payload,
    )

    celery_app.send_task(
        f"workers.tasks.{body.type}",
        kwargs={"job_id": str(job.id), **(body.payload or {})},
        task_id=str(uuid.uuid4()),
    )

    return job


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status: JobStatus | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    jobs = await jobs_repo.list_jobs(db, status=status, limit=limit, offset=offset)
    return JobListResponse(
        jobs=[JobResponse.model_validate(j) for j in jobs],
        total=len(jobs),
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    job = await jobs_repo.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
