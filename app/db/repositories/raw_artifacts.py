import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.raw_artifact import RawArtifact


async def create_raw_artifact(
    session: AsyncSession,
    *,
    task_run_id: uuid.UUID,
    content_hash: str,
    storage_path: str | None = None,
    raw_data: dict | None = None,
) -> RawArtifact:
    artifact = RawArtifact(
        task_run_id=task_run_id,
        content_hash=content_hash,
        storage_path=storage_path,
        raw_data=raw_data,
    )
    session.add(artifact)
    await session.flush()
    return artifact


async def get_by_content_hash(
    session: AsyncSession,
    content_hash: str,
) -> RawArtifact | None:
    stmt = select(RawArtifact).where(RawArtifact.content_hash == content_hash)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_raw_artifact(
    session: AsyncSession,
    artifact_id: uuid.UUID,
) -> RawArtifact | None:
    return await session.get(RawArtifact, artifact_id)
