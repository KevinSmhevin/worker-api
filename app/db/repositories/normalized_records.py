import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.normalized_record import NormalizedRecord


async def create_normalized_record(
    session: AsyncSession,
    *,
    raw_artifact_id: uuid.UUID | None = None,
    card_name: str | None = None,
    set_name: str | None = None,
    card_number: str | None = None,
    grading_company: str | None = None,
    grade: str | None = None,
    price: float | None = None,
    currency: str = "USD",
    sold_date=None,
    listing_url: str | None = None,
    image_url: str | None = None,
    source: str = "",
    content_hash: str = "",
    raw_title: str | None = None,
) -> NormalizedRecord:
    record = NormalizedRecord(
        raw_artifact_id=raw_artifact_id,
        card_name=card_name,
        set_name=set_name,
        card_number=card_number,
        grading_company=grading_company,
        grade=grade,
        price=price,
        currency=currency,
        sold_date=sold_date,
        listing_url=listing_url,
        image_url=image_url,
        source=source,
        content_hash=content_hash,
        raw_title=raw_title,
    )
    session.add(record)
    await session.flush()
    return record


async def bulk_create_normalized_records(
    session: AsyncSession,
    records: list[dict],
) -> list[NormalizedRecord]:
    objects = [NormalizedRecord(**record) for record in records]
    session.add_all(objects)
    await session.flush()
    return objects


async def get_by_content_hash(
    session: AsyncSession,
    content_hash: str,
) -> NormalizedRecord | None:
    stmt = select(NormalizedRecord).where(
        NormalizedRecord.content_hash == content_hash
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def exists_by_content_hash(
    session: AsyncSession,
    content_hash: str,
) -> bool:
    record = await get_by_content_hash(session, content_hash)
    return record is not None


async def list_records(
    session: AsyncSession,
    *,
    source: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[NormalizedRecord]:
    stmt = (
        select(NormalizedRecord)
        .order_by(NormalizedRecord.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if source:
        stmt = stmt.where(NormalizedRecord.source == source)
    result = await session.execute(stmt)
    return list(result.scalars().all())
