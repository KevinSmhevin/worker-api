import asyncio

from app.celery_app import celery_app
from app.core.constants import JobStatus
from app.core.exceptions import NonRetryableError, RetryableError
from app.core.logging import get_logger
from app.core.retry import get_celery_retry_kwargs

logger = get_logger(__name__)

_retry_kwargs = get_celery_retry_kwargs("scrape_ebay_sold")


@celery_app.task(
    name="adapters.ebay.scrape_sold_listings",
    bind=True,
    autoretry_for=(RetryableError,),
    **_retry_kwargs,
)
def scrape_ebay_sold_listings(
    self,
    job_id: str,
    url: str,
    seller: str | None = None,
):
    """Celery task: orchestrate eBay sold listings scrape end-to-end."""
    logger.info("ebay_scrape_start", job_id=job_id, url=url, seller=seller)

    try:
        result = asyncio.get_event_loop().run_until_complete(
            _run_scrape(job_id, url, seller)
        )
        return result
    except NonRetryableError:
        logger.error("ebay_scrape_non_retryable", job_id=job_id, exc_info=True)
        raise
    except RetryableError:
        logger.warning("ebay_scrape_retryable", job_id=job_id, exc_info=True)
        raise
    except Exception as exc:
        logger.error("ebay_scrape_unexpected", job_id=job_id, exc_info=True)
        raise RetryableError(str(exc)) from exc


async def _run_scrape(job_id: str, url: str, seller: str | None) -> dict:
    import uuid

    from app.adapters.registry import get_adapter
    from app.core.constants import Source
    from app.db.repositories import jobs as jobs_repo
    from app.db.repositories import normalized_records as records_repo
    from app.db.repositories import task_runs as task_runs_repo
    from app.db.session import async_session_factory
    from app.services.artifact_service import store_raw_html

    adapter = get_adapter(Source.EBAY)

    async with async_session_factory() as session:
        job_uuid = uuid.UUID(job_id)

        await jobs_repo.update_job_status(session, job_uuid, status=JobStatus.RUNNING)

        task_run = await task_runs_repo.create_task_run(
            session, job_id=job_uuid, task_name="scrape_ebay_sold_listings"
        )

        try:
            raw_html = await adapter.fetch(url, seller=seller)

            artifact_id, is_duplicate = await store_raw_html(
                session,
                task_run_id=task_run.id,
                html=raw_html,
                source=Source.EBAY,
                url=url,
            )

            raw_records = adapter.parse(raw_html)
            normalized = adapter.normalize(raw_records)

            persisted_count = 0
            for record in normalized:
                existing = await records_repo.get_by_content_hash(
                    session, record.content_hash
                )
                if not existing:
                    await records_repo.create_normalized_record(
                        session, **record.model_dump()
                    )
                    persisted_count += 1

            await task_runs_repo.mark_task_run_success(session, task_run.id)
            await jobs_repo.update_job_status(
                session, job_uuid, status=JobStatus.COMPLETED
            )
            await session.commit()

            logger.info(
                "ebay_scrape_complete",
                job_id=job_id,
                raw_count=len(raw_records),
                normalized_count=len(normalized),
                persisted_count=persisted_count,
                is_duplicate_html=is_duplicate,
            )

            return {
                "job_id": job_id,
                "status": "completed",
                "raw_count": len(raw_records),
                "normalized_count": len(normalized),
                "persisted_count": persisted_count,
            }

        except Exception as exc:
            await task_runs_repo.mark_task_run_failed(
                session, task_run.id, error_message=str(exc)
            )
            await jobs_repo.update_job_status(
                session,
                job_uuid,
                status=JobStatus.FAILED,
                error_message=str(exc),
            )
            await session.commit()
            raise
