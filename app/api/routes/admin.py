import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.celery_app import celery_app
from app.db.repositories import jobs as jobs_repo
from app.schemas.api.jobs import JobResponse
from app.schemas.domain.scrape_request import ScrapeRequest

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/scrape", response_model=JobResponse, status_code=202)
async def trigger_scrape(body: ScrapeRequest, db: AsyncSession = Depends(get_db)):
    """Manually trigger a one-off scrape job for dev/admin use."""
    job = await jobs_repo.create_job(
        db,
        job_type=f"scrape_{body.source}_sold",
        payload={
            "source": body.source,
            "url": body.url,
            "seller": body.seller,
            **(body.options or {}),
        },
    )

    celery_app.send_task(
        f"adapters.{body.source}.scrape_sold_listings",
        kwargs={
            "job_id": str(job.id),
            "url": body.url,
            "seller": body.seller,
        },
        task_id=str(uuid.uuid4()),
    )

    return job
