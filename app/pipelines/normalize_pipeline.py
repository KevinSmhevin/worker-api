from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.base import BaseAdapter
from app.core.logging import get_logger
from app.db.repositories import normalized_records as records_repo
from app.schemas.domain.normalized_record import NormalizedRecordSchema
from app.schemas.domain.raw_record import RawRecord

logger = get_logger(__name__)


async def run_normalize(
    session: AsyncSession,
    *,
    adapter: BaseAdapter,
    raw_records: list[RawRecord],
) -> list[NormalizedRecordSchema]:
    """Normalize pipeline: normalize raw records and deduplicate.

    Returns only records that don't already exist in the database.
    """
    normalized = adapter.normalize(raw_records)

    new_records: list[NormalizedRecordSchema] = []
    duplicate_count = 0

    for record in normalized:
        exists = await records_repo.exists_by_content_hash(session, record.content_hash)
        if exists:
            duplicate_count += 1
        else:
            new_records.append(record)

    logger.info(
        "normalize_complete",
        total=len(normalized),
        new=len(new_records),
        duplicates=duplicate_count,
    )

    return new_records
