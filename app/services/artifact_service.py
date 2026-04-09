import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.repositories import raw_artifacts as artifact_repo
from app.services.dedupe_service import compute_raw_html_hash
from app.services.storage_service import save_artifact

logger = get_logger(__name__)


async def store_raw_html(
    session: AsyncSession,
    *,
    task_run_id: uuid.UUID,
    html: str,
    source: str,
    url: str,
) -> tuple[uuid.UUID | None, bool]:
    """Store raw HTML artifact. Returns (artifact_id, is_duplicate).

    If the content hash already exists, returns the existing artifact's id
    and is_duplicate=True. Otherwise creates a new artifact.
    """
    content_hash = compute_raw_html_hash(html)

    existing = await artifact_repo.get_by_content_hash(session, content_hash)
    if existing:
        logger.info(
            "artifact_duplicate",
            content_hash=content_hash,
            existing_id=str(existing.id),
        )
        return existing.id, True

    storage_path = f"raw_html/{source}/{content_hash}.html"
    await save_artifact(html, path=storage_path)

    artifact = await artifact_repo.create_raw_artifact(
        session,
        task_run_id=task_run_id,
        content_hash=content_hash,
        storage_path=storage_path,
    )

    logger.info("artifact_stored", artifact_id=str(artifact.id), path=storage_path)
    return artifact.id, False
