from app.core.logging import get_logger
from app.schemas.domain.normalized_record import NormalizedRecordSchema

logger = get_logger(__name__)


async def run_index(records: list[NormalizedRecordSchema]) -> int:
    """Index pipeline: placeholder for future search indexing.

    Will push normalized records to Elasticsearch/Meilisearch
    for full-text search support.
    """
    logger.info("index_pipeline_noop", count=len(records))
    return len(records)
